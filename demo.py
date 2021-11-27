import ffbot


# Yahoo league/team id
# Visit your team at https://football.fantasysports.yahoo.com/f1/, and the url will also include your league and team ID
LEAGUE = 123456
TEAM = 1
POSITIONS = "QB, WR, WR, WR, RB, RB, TE, W/R/T, K, DEF, BN, BN, BN, BN, IR"
week = ffbot.current_week()

# Scrape data for current and available players, and their point forecasts for each week
df = ffbot.scrape(LEAGUE)

# Optional save data to CSV, and load latest data
# ffbot.save(df, week)
# df, week = ffbot.load()

# Optimize the assignment of players to positions each week to maximize remaining season discounted total points
# (points this week are worth more than points in future weeks)
#  decides which players to add and drop
#  optimization is repeated for current roster, for one player add/drop, two player add/drops, etc.
df_opt = ffbot.optimize(df, week, TEAM, POSITIONS)
pd.options.display.float_format = "{:+,.2f}".format  # number display format
print(df_opt)
