import csv
from os import listdir
from os.path import getctime, isfile, join, split
import re

from pulp import LpBinary, LpContinuous, LpMaximize, LpProblem, LpStatus, lpSum, LpVariable, value
from tabulate import tabulate


def optimize():
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

    # Find latest csv file
    folder = join('.', 'data')
    files = [f for f in listdir(folder) if isfile(join(folder, f))]
    latest_file = max([join(folder, f) for f in files], key=getctime)
    latest_filename = split(latest_file)[1]

    # Pre-process data
    current_week = re.findall(r'\d+', latest_filename)[-1]
    current_week = int(current_week)
    TIMES = [t for t in range(current_week, 18)]
    #  parse CSV file
    PLAYERS = []
    Names = dict()
    Position = dict()
    Roster0 = dict()
    Owner = dict()
    Projections = dict()
    with open(latest_file) as csvfile:
        for row in csv.reader(csvfile):
            p = row[0]
            PLAYERS.append(p)
            Names[p] = row[1]
            Position[p] = row[3]
            Roster0[p] = True if row[4] == 'True' else False
            Owner[p] = row[5]
            for t in TIMES:
                Projections[p, t] = float(row[5 + t])
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
    points = LpVariable.dicts('points', PlayerTime, lowBound=0, cat=LpContinuous)
    points_total = LpVariable.dicts('points total', PLAYERS, lowBound=0, cat=LpContinuous)
    discounted_points_total = LpVariable.dicts('discounted points total', PLAYERS, lowBound=0, cat=LpContinuous)

    # Define objective function
    prob += lpSum(discounted_points_total[p] for p in PLAYERS)

    # Define constraints
    prob += lpSum(roster[p] for p in PLAYERS) <= MAX_PLAYERS
    prob += MAX_PLAYERS <= lpSum(roster[p] for p in PLAYERS if Roster0[p]), 'max_drops'
    prob += 0 == lpSum(roster[p] for p in PLAYERS
                    if not Roster0[p] and Owner[p] != 'FA'), 'only_add_free_agents'
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
        prob.constraints['max_drops'].constant = -MAX_PLAYERS + 1 + drops
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
    while True:
        prob.constraints['max_drops'].constant = -MAX_PLAYERS + 1 + drops
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
