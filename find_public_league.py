from io import StringIO
from time import sleep

from pandas import read_html

from ffbot.scraper import create_session, generate_user_agent

s = create_session()

found_public, found_public_idp = False, False
for public_league in range(0, 1000):
    url = "https://football.fantasysports.yahoo.com/f1/{}/settings".format(public_league)
    s.headers["User-Agent"] = generate_user_agent()
    r = s.get(url)

    # Parse tables from page, if tables exist (i.e. public league)
    try:
        dfs = read_html(StringIO(r.text))
    except ValueError as e:
        if str(e) == "No tables found":
            print(f"{public_league} is not a valid public league")
            sleep(10)
            continue
        else:
            raise e

    # Parse league settings to detect if is DEF or IDP
    df = dfs[0]
    positions = df.loc[df["Setting"] == "Roster\xa0Positions:", "Value"].iloc[0]
    if "DEF" in positions:
        found_public = True
        print(f"{public_league} is a valid public league")
    elif "DB" in positions:
        found_public_idp = True
        print(f"{public_league} is a valid public IDP league")

    if found_public and found_public_idp:
        break
