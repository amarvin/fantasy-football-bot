from urllib.parse import parse_qsl, urlencode, urlparse

import requests
from bs4 import BeautifulSoup as bs
from loguru import logger
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from user_agent import generate_user_agent

# A public league for current week and player IDs
PUBLIC_LEAGUE = 76554


def create_session():
    """Create requests session with retries and random user-agent"""
    s = requests.Session()
    s.headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        "User-Agent": generate_user_agent(),
    }
    #  add retry loop
    retry = Retry(backoff_factor=0.6, status_forcelist=[500, 502, 503, 504, 999])
    adapter = HTTPAdapter(max_retries=retry)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    return s


def current_week():
    """Current season week"""
    logger.info("Scraping current season week")
    # Parse current week from a public league
    s = create_session()
    url = "https://football.fantasysports.yahoo.com/f1/{}".format(PUBLIC_LEAGUE)
    r = s.get(url)
    soup = bs(r.text, "lxml")
    span = soup.select_one("li.Navitem.current a.Navtarget")
    week = span.text.split()[1]
    week = int(week)

    return week
