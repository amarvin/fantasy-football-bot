# fantasy-football-bot (ffbot)

[![PyPI Latest Release](https://img.shields.io/pypi/v/ffbot.svg)](https://pypi.org/project/ffbot/)
[![PyPI downloads](https://static.pepy.tech/badge/ffbot)](https://pepy.tech/project/ffbot)
[![License](https://img.shields.io/github/license/amarvin/fantasy-football-bot)](https://github.com/amarvin/fantasy-football-bot/blob/main/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![codecov](https://codecov.io/gh/amarvin/fantasy-football-bot/branch/main/graph/badge.svg?token=CH6M9DR7VX)](https://codecov.io/gh/amarvin/fantasy-football-bot)

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
Visit your team at <https://football.fantasysports.yahoo.com/f1/>, and the url will also include your league and team ID.

```python
>>> LEAGUE = 123456
>>> TEAM = 1
>>> POSITIONS = "QB, WR, WR, WR, RB, RB, TE, W/R/T, K, DEF, BN, BN, BN, BN, IR"
>>> week = ffbot.current_week()
>>> df = ffbot.scrape(LEAGUE)
>>> # If playing an Individual Defensive Player (IDP) league, then scrape additional players with:
>>> # df = ffbot.scrape(LEAGUE, is_IDP=True)
Scraping all QB...
Scraping all WR...
Scraping all RB...
Scraping all TE...
Scraping all K...
Scraping all DEF...
Scraping weekly forecasts...
Total runtime: 0:10:33.784455
```

Optional methods to save data to CSV, and load data:

```python
>>> ffbot.save(df, week)
>>> df, week = ffbot.load()  # loads latest file, but you can also provide a filepath
```

### Optimize add and drop players

`ffbot.optimize()` is used to find players to add and drop that maximize your team's performance.
The optimizer decides which players to add and drop, and how to assign each player to positions each week.
Optimization is repeated for current roster, for one player add/drop, two player add/drops, etc.

```python
>>> df_opt = ffbot.optimize(df, week, TEAM, POSITIONS)
>>> print(df_opt)
                              Add              Drop Total points Discounted points     VOR
0                <current roster>                        1583.94            367.51  226.73
1                     Kansas City                          16.27              2.24   -7.98
2                     Matt Bryant         Joey Slye          4.6              1.67   -3.63
3                  Dede Westbrook      Kenyan Drake         4.27              0.65    2.75
4 Jordan Howard - Waivers (Oct 2)  Marvin Jones Jr.        10.37             17.23   -3.54
```

which means that optimal weekly rosters of your current players scores 1583.94 points
across the season and 367.51 discounted points (points in week 1 are worth more than week 12).
The best free agent to add is Kansas City, which increases discounted points by 2.24 (although lowers total season points by 16.27 and lowers value over replacement by 7.98).
Two other free agent pickups improve discounted points.
Only one Waiver claim (for Jordon Howard) increases discounted points.

## Contribution

Please add Issues or submit Pull Requests!

For local development, install optional testing dependencies and pre-commit hooks using

```sh
pip install ffbot[test]
pre-commit install
```
