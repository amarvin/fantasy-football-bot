import numpy as np
from pulp import LpBinary, LpContinuous, LpMaximize, LpProblem, LpStatus, lpSum, LpVariable, value
from tabulate import tabulate


def optimize(df, week, team):
    '''Optimize player pick-ups from free agents and waivers
    '''

    # Settings
    weekly_points_interest_rate = 0.4

    # Game rules
    MAX_PLAYERS = 14
    POSITIONS = ['QB', 'WR', 'RB', 'TE', 'W/R/T', 'K', 'DEF']
    PossiblePositions = [
        ('QB', 'QB'),
        ('WR', 'WR'),
        ('WR', 'W/R/T'),
        ('RB', 'RB'),
        ('RB', 'W/R/T'),
        ('TE', 'TE'),
        ('TE', 'W/R/T'),
        ('K', 'K'),
        ('DEF', 'DEF'),
        ('WR,TE', 'WR'),
        ('WR,TE', 'TE'),
        ('WR,TE', 'W/R/T')
    ]
    PositionMax = {'QB': 1, 'WR': 3, 'RB': 2, 'TE': 1, 'W/R/T': 1, 'K': 1, 'DEF': 1}

    # Pre-process data
    TIMES = [t for t in range(week, 18)]
    PLAYERS = []
    Names = dict()
    Position = dict()
    Roster0 = dict()
    Owner = dict()
    FreeAgent = dict()
    Available = dict()
    Projections = dict()
    for _, row in df.iterrows():
        p = row['ID']
        PLAYERS.append(p)
        Names[p] = row['Name']
        Position[p] = row['Position']
        Roster0[p] = True if row['Owner ID'] == team else False
        owner = row['Owner']
        Owner[p] = owner
        FreeAgent[p] = True if np.isnan(row['Owner ID']) and owner == 'Free Agent' else False
        Available[p] = True if np.isnan(row['Owner ID']) else False
        for t in TIMES:
            Projections[p, t] = float(row['Week {}'.format(t)])
    #  create other parameters
    n_roster0 = sum(1 for p in PLAYERS if Roster0[p])
    n_roster0 = min(n_roster0, MAX_PLAYERS)
    Discounts = {
        t: 1 / (1 + weekly_points_interest_rate) ** t_n
        for t_n, t in enumerate(TIMES)
    }
    PlayerTime = [(p, t) for p in PLAYERS for t in TIMES]
    PlayerPosition = [
        (p, n)
        for p in PLAYERS
        for n in POSITIONS
        if (Position[p], n) in PossiblePositions
    ]
    PlayerTimePosition = [
        (p, t, n)
        for p in PLAYERS
        for t in TIMES
        for n in POSITIONS
        if (p, n) in PlayerPosition
    ]

    # Define optimization problem
    prob = LpProblem('football', LpMaximize)

    # Define decision variables
    roster = LpVariable.dicts('roster', PLAYERS, cat=LpBinary)
    assign = LpVariable.dicts('assign', PlayerTimePosition, cat=LpBinary)
    points = LpVariable.dicts('points', PlayerTime, cat=LpContinuous)
    points_total = LpVariable.dicts('points total', PLAYERS, cat=LpContinuous)
    discounted_points_total = LpVariable.dicts('discounted points total', PLAYERS, cat=LpContinuous)

    # Define objective function
    prob += lpSum(discounted_points_total[p] for p in PLAYERS)

    # Define constraints
    prob += lpSum(roster[p] for p in PLAYERS) <= MAX_PLAYERS
    prob += n_roster0 <= lpSum(roster[p] for p in PLAYERS if Roster0[p]), 'max_drops'
    prob += 0 == lpSum(roster[p] for p in PLAYERS if not Roster0[p] and not FreeAgent[p]), 'only_add_free_agents'
    for p, t in PlayerTime:
        prob += roster[p] >= lpSum(assign[p, t, n] for n in POSITIONS if (p, n) in PlayerPosition)
        prob += points[p, t] == Projections[p, t] * lpSum(assign[p, t, n] for n in POSITIONS if (p, n) in PlayerPosition)
        prob += lpSum(assign[p, t, n] for n in POSITIONS if (p, n) in PlayerPosition) <= 1
    for p in PLAYERS:
        prob += points_total[p] == lpSum(points[p, t] for t in TIMES)
        prob += discounted_points_total[p] == lpSum(Discounts[t] * points[p, t] for t in TIMES)
    for t in TIMES:
        for n in POSITIONS:
            prob += lpSum(assign[p, t, n] for p in PLAYERS if (p, n) in PlayerPosition) <= PositionMax[n]

    # Solve optimization problem
    solutions_headers = ['Add', 'Drop', 'Total points', 'Discounted points']
    solutions = []
    prob.solve()
    assert LpStatus[prob.status] == 'Optimal'
    total_points = sum(points_total[p].varValue for p in PLAYERS)
    discounted_points = value(prob.objective)
    solutions.append(['', '', total_points, discounted_points])
    last_total_points = total_points
    last_discounted_points = discounted_points

    # Re-solve for adding each free agent
    skip_players = []
    drops = 0
    while True:
        prob.constraints['max_drops'].constant = -n_roster0 + 1 + drops
        prob.solve()
        assert LpStatus[prob.status] == 'Optimal'
        drop = ''
        add = ''
        for p in PLAYERS:
            if p in skip_players:
                continue
            roster1 = roster[p].varValue
            if Roster0[p] and not roster1:
                drop = Names[p]
                prob += roster[p] == 0
                skip_players.append(p)
            elif not Roster0[p] and roster1:
                add = Names[p]
                prob += roster[p] == 1
                skip_players.append(p)
        if add == '' and drop == '':
            break
        drops += 1
        total_points = sum(points_total[p].varValue for p in PLAYERS)
        discounted_points = value(prob.objective)
        solutions.append([add, drop, total_points - last_total_points, discounted_points - last_discounted_points])
        last_total_points = total_points
        last_discounted_points = discounted_points


    # Re-solve for adding each waiver claim
    del prob.constraints['only_add_free_agents']
    prob += 0 == lpSum(roster[p] for p in PLAYERS if not Roster0[p] and not Available[p]), 'only_add_available'
    while True:
        prob.constraints['max_drops'].constant = -n_roster0 + 1 + drops
        prob.solve()
        assert LpStatus[prob.status] == 'Optimal'
        drop = ''
        add = ''
        for p in PLAYERS:
            if p in skip_players:
                continue
            roster1 = roster[p].varValue
            if Roster0[p] and not roster1:
                drop = Names[p]
                prob += roster[p] == 0
                skip_players.append(p)
            elif not Roster0[p] and roster1:
                add = Names[p] + ' - ' + Owner[p]
                prob += roster[p] == 1
                skip_players.append(p)
        if add == '' and drop == '':
            break
        drops += 1
        total_points = sum(points_total[p].varValue for p in PLAYERS)
        discounted_points = value(prob.objective)
        solutions.append([add, drop, total_points - last_total_points, discounted_points - last_discounted_points])
        last_total_points = total_points
        last_discounted_points = discounted_points

    # Print results
    print(tabulate(solutions, solutions_headers, floatfmt='+.2f'))
