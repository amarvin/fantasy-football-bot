import logging
from datetime import datetime
from json.decoder import JSONDecodeError
from urllib.parse import parse_qsl, urlencode, urlparse

import numpy as np
import pandas as pd
import requests
import scrapy
from loguru import logger
from scrapy.crawler import CrawlerProcess
from scrapy.downloadermiddlewares.retry import get_retry_request
from scrapy.selector import Selector

try:
    from .scraper import current_week
except ImportError:
    from scraper import current_week

# A public league for current week and player IDs
PUBLIC_LEAGUE = 76554

logging.getLogger("filelock").setLevel(logging.WARNING)
logging.getLogger("scrapy").setLevel(logging.DEBUG)
logging.getLogger("scrapy").propagate = False


def get_proxy_list():
    response = requests.get("https://www.sslproxies.org")
    df = pd.read_html(response.text)[0]
    df = df[df["Code"].isin(["DE", "GB", "US"])]
    df["proxy"] = "https://" + df["IP Address"] + ":" + df["Port"].astype(str)
    return df["proxy"].to_list()


class ProjectionScraper(scrapy.Spider):
    name = "current_week"
    custom_settings = dict(
        AUTOTHROTTLE_ENABLED=True,
        COOKIES_ENABLED=False,
        # DOWNLOAD_DELAY=2,
        DOWNLOADER_MIDDLEWARES={
            "rotating_proxies.middlewares.RotatingProxyMiddleware": 610,
            "rotating_proxies.middlewares.BanDetectionMiddleware": 620,
            "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
            "scrapy.downloadermiddlewares.retry.RetryMiddleware": None,
            "scrapy_fake_useragent.middleware.RandomUserAgentMiddleware": 400,
            "scrapy_fake_useragent.middleware.RetryUserAgentMiddleware": 401,
        },
        REQUEST_FINGERPRINTER_IMPLEMENTATION="2.7",
        ROTATING_PROXY_LIST=get_proxy_list(),
    )
    groups = ["QB", "WR", "RB", "TE", "K", "DEF"]
    # groups = ["RB"]
    start_urls = [
        "https://football.fantasysports.yahoo.com/f1/{}/players?".format(PUBLIC_LEAGUE)
        + urlencode(
            dict(
                count=0,
                pos=group,
                sort="PR_S",  # sort by projected season rank
                stat1="K_K",  # ranks
                status="ALL",
            )
        )
        for group in groups
    ]

    def start_requests(self):
        logger.info("Scraping all player projections...")
        return super().start_requests()

    def parse(self, response):
        table = response.css("#players-table table")
        rows = table.css("tbody tr")
        for row in rows:
            td = row.css("td")[1]
            ID = td.css("span.player-status a").attrib["data-ys-playerid"]
            ID = int(ID)
            team = td.css(".ysf-player-name span::text").get()
            team = team.split()[0]
            self.data[ID] = {"Team": team}

            params = {"pid": ID}
            url_player_projection = (
                "https://football.fantasysports.yahoo.com/f1/{}/playernote?".format(
                    self.league
                )
                + urlencode(params)
            )
            yield response.follow(
                url=url_player_projection, callback=self.parse_player, meta=params
            )

        if rows:
            # Request next 25 players
            url = urlparse(response.url)
            params = dict(parse_qsl(url.query))
            params["count"] = int(params["count"]) + 25
            url = url._replace(query=urlencode(params))
            yield response.follow(url=url.geturl(), callback=self.parse)

    def parse_player(self, response):
        ID = response.meta.get("pid")
        try:
            html_string = response.json()["content"]
        except JSONDecodeError:
            new_request_or_none = get_retry_request(
                response.request,
                spider=self,
                reason="JSONDecodeError",
            )
            return new_request_or_none

        html = Selector(text=html_string)

        # Player info
        playerinfo = html.css(".playerinfo")
        self.data[ID].update(
            Name=playerinfo.css(".name::text").get(),
            # Team=playerinfo.css('.player-team-name::text').get(),
            Position=playerinfo.css("dd.pos::text").get(),
            Owner=playerinfo.css("dd.owner a::text").get(),
        )

        # Owner ID
        a = playerinfo.css("dd.owner a")
        if a:
            self.data[ID]["Owner ID"] = int(a.attrib["href"].split("/")[-1])
        else:
            self.data[ID]["Owner ID"] = np.nan

        # Status
        status = playerinfo.css(".status::text")
        self.data[ID]["Status"] = status if status else np.nan
        self.data[ID]["% Owned"] = playerinfo.css("dd.owned::text").get().split()[0]

        # Weekly projections
        df2 = pd.read_html(html.get())[0]
        for _, row2 in df2.iterrows():
            week = "Week {}".format(row2["Week"])
            points = row2["Fan Pts"]
            if points[0] == "*":
                # Game hasn't occured yet
                self.data[ID][week] = float(points[1:])
                # self.data[ID][week + ' projection'] = float(points[1:])
                # self.data[ID][week + ' actual'] = np.nan
            elif points == "-":
                # Bye week
                self.data[ID][week] = 0
                # self.data[ID][week + ' projection'] = 0
                # self.data[ID][week + ' actual'] = 0
            else:
                # Game completed
                self.data[ID][week] = float(points)
                # self.data[ID][week + ' projection'] = np.nan
                # self.data[ID][week + ' actual'] = float(points)


def scrape(league):
    # Start timer
    startTime = datetime.now()

    # Start crawler
    crawler = CrawlerProcess()
    data = {}
    crawler.crawl(ProjectionScraper, data=data, league=league)
    crawler.start()

    # Create dataframe
    df = pd.DataFrame.from_dict(data, orient="index")
    df.reset_index(inplace=True)
    df.rename(columns={"index": "ID"}, inplace=True)

    # Reorder columns
    columns = list(df.columns)
    columns[2], columns[1] = columns[1], columns[2]
    df = df[columns]

    # Calculate VOR
    columns = ["Week {}".format(i) for i in range(current_week(), 18)]
    df["Remaining"] = df[columns].sum(axis=1)
    available = df.loc[df["Owner ID"].isnull()]
    means = available.groupby(["Position"])["Remaining"].nlargest(3).mean(level=0)
    logger.info("Total runtime: {}".format(datetime.now() - startTime))
    df["VOR"] = df.apply(
        lambda row: row["Remaining"]
        - max(means[n.strip()] for n in row["Position"].split(",")),
        axis=1,
    )
    df.sort_values(by="VOR", ascending=False, inplace=True)
    df = df.round(2)

    return df


if __name__ == "__main__":
    print(scrape(809120))
