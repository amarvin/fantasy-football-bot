# fantasy-football-bot (ffbot)
Automate playing Yahoo Fantasy Football

# Installation
- `pip install ffbot`
- requires downloading [ChromeDriver](http://chromedriver.chromium.org)

# Usage
```python
from ffbot import optimize, scrape

# Yahoo credentials and league/team id
# Visit your team at https://football.fantasysports.yahoo.com/f1/, and the url will also include your league and team ID
credentials = dict(
    username='your_yahoo_fantasy_username',
    password='your_yahoo_fantasy_password',
    league=123456,
    team=1,
)

# Scrape data for current and available players, and their point forecasts for each week
scrape(credentials)

# Optimize the assignment of players to positions each week to maximize remaining season discounted total points (points this week are worth more than points in future weeks)
#  decides which players to add and drop
#  optimization is repeated for current roster, for one player add/drop, two player add/drops, etc.
optimize()
```

# Contribution
Please add Issues or submit Pull requests!
