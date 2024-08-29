import re
from datetime import datetime
from io import StringIO

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from loguru import logger
from requests.adapters import HTTPAdapter
from tqdm import tqdm
from urllib3.util import Retry
from user_agent import generate_user_agent

# A public league for current week and player IDs
PUBLIC_LEAGUE = 101
PUBLIC_LEAGUE_IDP = 413
SEARCH_PLAYER_GROUPS = ["QB", "WR", "RB", "TE", "K", "DEF"]
SEARCH_PLAYER_GROUPS_IDP = ["QB", "WR", "RB", "TE", "K", "D", "DB", "DL", "LB"]


def create_session():
    """Create requests session with retries and random user-agent"""
    s = requests.Session()
    s.headers = {
        "Accept": "text/html",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US",
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        "User-Agent": generate_user_agent(),
    }
    #  add retry loop
    retry = Retry(backoff_factor=0.6, status_forcelist=[500, 502, 503, 504, 999])
    adapter = HTTPAdapter(max_retries=retry)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    return s


def scrape(league, is_IDP: bool = False):
    """Scrape data

    :param league: league ID
    :param is_IDP: (bool) is this a individual defense player (IDP) league?
    """

    # Start timer
    startTime = datetime.now()

    # Scrape player IDs and teams from a public league
    data = set()
    groups = SEARCH_PLAYER_GROUPS_IDP if is_IDP else SEARCH_PLAYER_GROUPS
    s = create_session()
    for group in groups:
        logger.info("Scraping all {}...".format(group))
        i = 0
        while True:
            # Request next 25 best players
            s.headers["User-Agent"] = generate_user_agent()
            r = s.get(
                "https://football.fantasysports.yahoo.com/f1/{}/players".format(
                    PUBLIC_LEAGUE_IDP if is_IDP else PUBLIC_LEAGUE
                ),
                params=dict(
                    count=i * 25,
                    pos=group,
                    sort="PR_S",  # sort by projected season rank
                    stat1="K_K",  # ranks
                    status="ALL",
                ),
            )
            i += 1
            soup = bs(r.text, "lxml")
            table = soup.select_one("#players-table table")
            if not table:
                break
            rows = table.select("tbody tr")
            if not rows:
                break
            for row in rows:
                td = row.select("td")[1]
                ID = td.select_one(".player-status a")["data-ys-playerid"]
                ID = int(ID)
                team = td.select_one(".ysf-player-name span").text
                team = team.split()[0]
                data.add((ID, team))

    # Create dataframe
    df = pd.DataFrame(data, columns=["ID", "Team"])

    # Scrape projections
    def get_projections(row):
        # New session every 100 players
        global s
        if row.name % 100 == 0:
            s = create_session()

        pid = row["ID"]
        url = "https://football.fantasysports.yahoo.com/f1/{}/playernote".format(league)
        params = {"pid": pid}
        s.headers["User-Agent"] = generate_user_agent()
        r = s.get(url, params=params)
        html = r.json()["content"]
        soup = bs(html, "lxml")
        playerinfo = soup.select_one(".playerinfo")
        row["Name"] = playerinfo.select_one(".name").text
        # row['Team'] = playerinfo.select_one('.player-team-name').text
        row["Position"] = playerinfo.select_one("dd.pos").text[:-1]
        row["Owner"] = playerinfo.select_one("dd.owner").text[:-1]

        # Owner ID
        a = playerinfo.select_one("dd.owner a")
        if a:
            row["Owner ID"] = int(a["href"].split("/")[-1])
        else:
            row["Owner ID"] = np.nan

        # Status
        status = playerinfo.select_one(".status")
        if status:
            row["Status"] = status.text
        else:
            row["Status"] = np.nan

        row["% Owned"] = playerinfo.select_one("dd.owned").text.split()[0]

        # Weekly projections
        df2 = pd.read_html(StringIO(html))[0]
        for _, row2 in df2.iterrows():
            week = "Week {}".format(row2["Week"])
            points = row2["Fan Pts"]
            if points[0] == "*":
                # Game hasn't occured yet
                row[week] = float(points[1:])
                # row[week + ' projection'] = float(points[1:])
                # row[week + ' actual'] = np.nan
            elif points == "-":
                # Bye week
                row[week] = 0
                # row[week + ' projection'] = 0
                # row[week + ' actual'] = 0
            else:
                # Game completed
                row[week] = float(points)
                # row[week + ' projection'] = np.nan
                # row[week + ' actual'] = float(points)

        return row

    tqdm.pandas(desc="Scraping weekly forecasts")
    df = df.progress_apply(get_projections, axis=1)

    # Reorder columns
    columns = list(df.columns)
    columns[2], columns[1] = columns[1], columns[2]
    df = df[columns]

    # Calculate VOR
    columns = ["Week {}".format(i) for i in range(current_week(), 18)]
    df["Remaining"] = df[columns].sum(axis=1)
    available = df.loc[df["Owner ID"].isnull()]
    means = (
        available.groupby(["Position"])["Remaining"].nlargest(3).groupby(level=0).mean()
    )
    for positions in means.index:
        if "," in positions:
            for position in positions.split(","):
                position = position.strip()
                if position not in means:
                    means[position] = means[positions]
    df["VOR"] = df.apply(
        lambda row: row["Remaining"]
        - max(means[n.strip()] for n in row["Position"].split(",")),
        axis=1,
    )
    df.sort_values(by="VOR", ascending=False, inplace=True)
    df = df.round(2)

    logger.info("Total runtime: {}".format(datetime.now() - startTime))
    return df


def current_week():
    """Current season week"""

    # Parse current week from a public league
    s = create_session()
    url = "https://football.fantasysports.yahoo.com/f1/{}".format(PUBLIC_LEAGUE)
    s.headers["User-Agent"] = generate_user_agent()
    r = s.get(url)
    soup = bs(r.text, "lxml")
    matchups = soup.select_one("#matchupweek .matchups-body")
    weeks = re.findall(r"Week (\d+)", matchups.text)
    week = weeks[0]
    week = int(week)

    return week
