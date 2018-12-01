# fantasy-football-bot
Automate playing Yahoo Fantasy Football

# Usage
There are two components:
- `scraper.py`
  - web-scrapes the current and available players, and their point forecasts for the rest of the season
  - requires `credentials.json` with your Yahoo Fantasy Football credentials
  - requires downloading [ChromeDriver](http://chromedriver.chromium.org)
- `optimize.py`
  - optimize the assignment of players to positions each week to maximize remaining season discounted total points (points this week are worth more than points in future weeks)
  - decides which players to add and drop
  - optimization is repeated for current roster, for one player add/drop, two player add/drops, etc.

# Contribution
Please add Issues or submit Pull requests!
