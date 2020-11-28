# fantasy-football-bot (ffbot)

Automate playing Yahoo Fantasy Football

## Installation

```sh
pip install ffbot
```

## Usage

```python
>>> import ffbot
```

### Scrape player forecasts

To connect to your Yahoo league and team, you need your league ID and team ID.
Visit your team at https://football.fantasysports.yahoo.com/f1/, and the url will also include your league and team ID.

```python
>>> league = 123456
>>> team = 1
>>> positions = 'QB, WR, WR, WR, RB, RB, TE, W/R/T, K, DEF, BN, BN, BN, BN, IR'
>>> week = ffbot.current_week()
>>> df = ffbot.scrape(league)
Scraping all QB...
Scraping all WR...
Scraping all RB...
Scraping all TE...
Scraping all K...
Scraping all DEF...
Scraping weekly forecasts...
Total runtime: 0:10:33.784455
```

Optional methods to save data to CSV, and load latest data:

```python
>>> ffbot.save(df, week)
>>> df, week = ffbot.load()
```

### Optimize add and drop players

`ffbot.optimize()` is used to find players to add and drop that maximize your team's performance.
The optimizer decides which players to add and drop, and how to assign each player to positions each week.
Optimization is repeated for current roster, for one player add/drop, two player add/drops, etc.

```python
>>> ffbot.optimize(df, week, team, positions)
Add                              Drop                Total points    Discounted points      VOR
-------------------------------  ----------------  --------------  -------------------  -------
<current roster>                                         +1583.94              +367.51  +226.73
Kansas City                                                +16.27                +2.24    -7.98
Matt Bryant                      Joey Slye                  +4.60                +1.67    -3.63
Dede Westbrook                   Kenyan Drake               +4.27                +0.65    +2.75
Jordan Howard - Waivers (Oct 2)  Marvin Jones Jr.          +10.37               +17.23    -3.54
```

which means that optimal weekly rosters of your current players scores 1583.94 points
across the season and 367.51 discounted points (points in week 1 are worth more than week 12).
The best free agent to add is Kansas City, which increases discounted points by 2.24 (although lowers total season points by 16.27 and lowers value over replacement by 7.98).
Two other free agent pickups improve discounted points.
Only one Waiver claim (for Jordon Howard) increases discounted points.

## Contribution

Please add Issues or submit Pull requests!
