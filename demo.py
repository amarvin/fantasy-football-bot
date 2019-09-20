import json

from ffbot import optimize, scrape


# Read Yahoo credentials from json
with open('credentials.json') as f:
    credentials = json.load(f)

# Scrape data
scrape(credentials)

# Optimize player pick-ups from free agents and waivers
optimize()
