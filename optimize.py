import csv
from os import listdir
from os.path import getctime, isfile, join, split

from pulp import LpBinary, LpContinuous, LpMaximize, LpProblem, LpStatus, lpSum, LpVariable, value
from tabulate import tabulate


# Settings
weekly_points_interest_rate = 0.4
max_dropped_players = 3

# Game rules
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
    ('DEF', 'DEF')
]
PositionMax = {'QB': 1, 'WR': 3, 'RB': 2, 'TE': 1, 'W/R/T': 1, 'K': 1, 'DEF': 1}

# Find latest csv file
folder = join('.', 'data')
files = [f for f in listdir(folder) if isfile(join(folder, f))]
latest_file = max([join(folder, f) for f in files], key=getctime)
latest_filename = split(latest_file)[1]

# Pre-process data
current_week = int(latest_filename[1:-4])
TIMES = [t for t in range(current_week, 18)]
#  parse CSV file
PLAYERS = []
Names = dict()
Position = dict()
Roster0 = dict()
Projections = dict()
with open(latest_file) as csvfile:
    for row in csv.reader(csvfile):
        p = row[0]
        PLAYERS.append(p)
        Names[p] = row[1]
        Position[p] = row[3]
        Roster0[p] = float(row[4])
        for t in TIMES:
            Projections[p, t] = float(row[4 + t])
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
prob += lpSum(roster[p] for p in PLAYERS) <= 16
prob += 16 <= lpSum(roster[p] for p in PLAYERS if Roster0[p] == 1), 'max_drops'
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
skip_players = []
for i in range(max_dropped_players):
    prob.constraints['max_drops'].constant = -15 + i
    prob.solve()
    assert LpStatus[prob.status] == 'Optimal'
    for p in PLAYERS:
        if p in skip_players:
            continue
        roster0 = Roster0[p]
        roster1 = roster[p].varValue
        if roster0 and not roster1:
            drop = Names[p]
            skip_players.append(p)
        elif not roster0 and roster1:
            add = Names[p]
            skip_players.append(p)
    total_points = sum(points_total[p].varValue for p in PLAYERS)
    discounted_points = value(prob.objective)
    solutions.append([add, drop, total_points - last_total_points, discounted_points - last_discounted_points])
    last_total_points = total_points
    last_discounted_points = discounted_points
print(tabulate(solutions, solutions_headers, floatfmt='+.2f'))
