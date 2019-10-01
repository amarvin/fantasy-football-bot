from ffbot import optimize, scrape


# League and team IDs
league = 370820
team = 11

# Scrape data
scrape(league)

# Optimize player pick-ups from free agents and waivers
optimize(team)
