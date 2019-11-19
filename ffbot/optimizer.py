from collections import Counter
import math

from pulp import LpBinary, LpContinuous, LpMaximize, LpProblem, LpStatus, lpSum, LpVariable, value
from tabulate import tabulate


def optimize(df, week, team, positions):
    '''Optimize player pick-ups from free agents and waivers
    '''

    # Settings
    weekly_points_interest_rate = 0.4

    # Game rules
    positions = [x.strip() for x in positions.split(',')]
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
    PositionMax = Counter(positions)
    POSITIONS = PositionMax.keys()

    # Pre-process data
    TIMES = [t for t in range(week, 18)]
    PLAYERS = set()
    Names = dict()
    Position = dict()
    Roster0 = dict()
    Owner = dict()
    Status = dict()
    FreeAgent = dict()
    Available = dict()
    Projections = dict()
    VOR = dict()
    for _, row in df.iterrows():
        p = row['ID']
        PLAYERS.add(p)
        Names[p] = row['Name']
        Position[p] = row['Position']
        owner_id = row['Owner ID']
        Roster0[p] = owner_id == team
        owner = row['Owner']
        Owner[p] = owner
        Status[p] = row['Status']
        FreeAgent[p] = math.isnan(owner_id) and owner == 'Free Agent'
        Available[p] = math.isnan(owner_id)
        for t in TIMES:
            Projections[p, t] = float(row['Week {}'.format(t)])
        VOR[p] = row['VOR']
    #  create other parameters
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
    for p in PLAYERS:
        # All players take bench position
        PlayerPosition.append((p, 'BN'))
        # All injured players can take IR position
        if Status[p] in ['O', 'IR']:
            PlayerPosition.append((p, 'IR'))
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
    add = LpVariable.dicts('add', PLAYERS, cat=LpBinary)
    drop = LpVariable.dicts('drop', PLAYERS, cat=LpBinary)
    assign = LpVariable.dicts('assign', PlayerTimePosition, cat=LpBinary)
    points = LpVariable.dicts('points', PlayerTime, cat=LpContinuous)
    points_total = LpVariable.dicts('points total', PLAYERS, cat=LpContinuous)
    discounted_points_total = LpVariable.dicts('discounted points total', PLAYERS, cat=LpContinuous)

    # Define objective function
    prob += lpSum(discounted_points_total[p] for p in PLAYERS)

    # Define constraints
    prob += 0 >= lpSum(add[p] for p in PLAYERS), 'max_adds'
    prob += 0 == lpSum(add[p] for p in PLAYERS if not FreeAgent[p]), 'only_add_free_agents'
    for p, t in PlayerTime:
        prob += roster[p] == lpSum(assign[p, t, n] for n in POSITIONS if (p, n) in PlayerPosition)
        prob += points[p, t] == Projections[p, t] * lpSum(assign[p, t, n] for n in POSITIONS if (p, n) in PlayerPosition if n not in ['BN', 'IR'])
        prob += lpSum(assign[p, t, n] for n in POSITIONS if (p, n) in PlayerPosition) <= 1
    for p in PLAYERS:
        if not Roster0[p]:
            prob += drop[p] == 0
        if not Available[p]:
            prob += add[p] == 0
        prob += roster[p] == Roster0[p] + add[p] - drop[p]
        prob += points_total[p] == lpSum(points[p, t] for t in TIMES)
        prob += discounted_points_total[p] == lpSum(Discounts[t] * points[p, t] for t in TIMES)
    for t in TIMES:
        for n in POSITIONS:
            prob += lpSum(assign[p, t, n] for p in PLAYERS if (p, n) in PlayerPosition) <= PositionMax[n]

    # Solve optimization problem
    solutions_headers = ['Add', 'Drop', 'Total points', 'Discounted points', 'VOR']
    solutions = []
    prob.solve()
    assert LpStatus[prob.status] == 'Optimal'
    known_drops = set()
    n_drops = 0
    for p in PLAYERS:
        if drop[p].varValue:
            this_drop = Names[p]
            prob += drop[p] == 1
            known_drops.add(p)
            solutions.append(['', this_drop, None, None])
            n_drops += 1
    total_points = sum(points_total[p].varValue for p in PLAYERS)
    discounted_points = value(prob.objective)
    vor = sum(VOR[p] * roster[p].varValue for p in PLAYERS)
    solutions.append(['<current roster>', '', total_points, discounted_points, vor])
    last_total_points = total_points
    last_discounted_points = discounted_points
    last_vor = vor
    prob += n_drops >= lpSum(drop[p] for p in PLAYERS), 'max_drops'

    # Re-solve for each add without dropping any players
    known_adds = set()
    n_adds = 1
    while True:
        prob.constraints['max_adds'].constant = - n_adds
        prob.solve()
        assert LpStatus[prob.status] == 'Optimal'
        this_add = ''
        for p in PLAYERS:
            if add[p].varValue and p not in known_adds:
                this_add = Names[p]
                prob += add[p] == 1
                known_adds.add(p)
        if this_add == '':
            break
        n_adds += 1
        total_points = sum(points_total[p].varValue for p in PLAYERS)
        discounted_points = value(prob.objective)
        vor = sum(VOR[p] * roster[p].varValue for p in PLAYERS)
        solutions.append([this_add, '', total_points - last_total_points, discounted_points - last_discounted_points, vor - last_vor])
        last_total_points = total_points
        last_discounted_points = discounted_points
        last_vor = vor

    # Re-solve for each drop to acquire a free agent
    del prob.constraints['max_adds']
    while True:
        n_drops += 1
        prob.constraints['max_drops'].constant = - n_drops
        prob.solve()
        assert LpStatus[prob.status] == 'Optimal'
        this_drop = ''
        this_add = ''
        for p in PLAYERS:
            if drop[p].varValue and p not in known_drops:
                this_drop = Names[p]
                prob += drop[p] == 1
                known_drops.add(p)
            elif add[p].varValue and p not in known_adds:
                this_add = Names[p]
                prob += add[p] == 1
                known_adds.add(p)
                n_adds += 1
        if this_add == '' and this_drop == '':
            break
        total_points = sum(points_total[p].varValue for p in PLAYERS)
        discounted_points = value(prob.objective)
        vor = sum(VOR[p] * roster[p].varValue for p in PLAYERS)
        solutions.append([this_add, this_drop, total_points - last_total_points, discounted_points - last_discounted_points, vor - last_vor])
        last_total_points = total_points
        last_discounted_points = discounted_points
        last_vor = vor

    # Re-solve for each waiver claim add without dropping any players
    del prob.constraints['only_add_free_agents']
    prob += 0 >= lpSum(add[p] for p in PLAYERS), 'max_adds'
    while True:
        prob.constraints['max_adds'].constant = - n_adds
        prob.solve()
        assert LpStatus[prob.status] == 'Optimal'
        this_add = ''
        for p in PLAYERS:
            if add[p].varValue and p not in known_adds:
                this_add = Names[p] + ' - ' + Owner[p]
                prob += add[p] == 1
                known_adds.add(p)
        if this_add == '':
            break
        n_adds += 1
        total_points = sum(points_total[p].varValue for p in PLAYERS)
        discounted_points = value(prob.objective)
        vor = sum(VOR[p] * roster[p].varValue for p in PLAYERS)
        solutions.append([this_add, '', total_points - last_total_points, discounted_points - last_discounted_points, vor - last_vor])
        last_total_points = total_points
        last_discounted_points = discounted_points
        last_vor = vor

    # Re-solve for each drop to acquire a waiver claim
    del prob.constraints['max_adds']
    while True:
        prob.constraints['max_drops'].constant = - n_drops
        prob.solve()
        assert LpStatus[prob.status] == 'Optimal'
        this_drop = ''
        this_add = ''
        for p in PLAYERS:
            if drop[p].varValue and p not in known_drops:
                this_drop = Names[p]
                prob += drop[p] == 1
                known_drops.add(p)
            elif add[p].varValue and p not in known_adds:
                this_add = Names[p] + ' - ' + Owner[p]
                prob += add[p] == 1
                known_adds.add(p)
        if this_add == '' and this_drop == '':
            break
        n_drops += 1
        total_points = sum(points_total[p].varValue for p in PLAYERS)
        discounted_points = value(prob.objective)
        vor = sum(VOR[p] * roster[p].varValue for p in PLAYERS)
        solutions.append([this_add, this_drop, total_points - last_total_points, discounted_points - last_discounted_points, vor - last_vor])
        last_total_points = total_points
        last_discounted_points = discounted_points
        last_vor = vor

    # Print results
    print(tabulate(solutions, solutions_headers, floatfmt='+.2f'))
