from datetime import datetime
from time import sleep

from bs4 import BeautifulSoup as bs
import numpy as np
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


# A public league for current week and player IDs
PUBLIC_LEAGUE = 39345

# Create session
s = requests.Session()
s.headers = {
    'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
}
#  add retry loop
retry = Retry(
    total=10,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504, 999]
)
adapter = HTTPAdapter(max_retries=retry)
s.mount('http://', adapter)
s.mount('https://', adapter)


def scrape(league):
    '''Scrape data

    :param league: league ID
    '''

    # Start timer
    startTime = datetime.now()

    # Scrape player IDs from a public league
    IDs = set()
    groups = ['QB', 'WR', 'RB', 'TE', 'K', 'DEF']
    for group in groups:
        print('Scraping all {}...'.format(group))
        for i in range(3):
            # Request next 25 best players
            r = s.get(
                'https://football.fantasysports.yahoo.com/f1/{}/players'.format(PUBLIC_LEAGUE),
                params=dict(
                    count=i * 25,
                    pos=group,
                    sort='PR_S',  # sort by projected season rank
                    stat1='K_K',  # ranks
                    status='ALL',
                ),
            )
            soup = bs(r.text, 'lxml')
            table = soup.select_one('#players-table table')
            rows = table.select('tbody tr')
            if not rows: break
            for row in rows:
                ID = row.select('td')[1].select_one('span.player-status a')['data-ys-playerid']
                ID = int(ID)
                IDs.add(ID)

    # Create dataframe
    df = pd.DataFrame(IDs, columns=['ID'])

    # Scrape projections
    print('Scraping weekly forecasts...')
    def get_projections(row):
        pid = row['ID']
        url = 'https://football.fantasysports.yahoo.com/f1/{}/playernote?pid={}'.format(league, pid)
        r = s.get(url)
        html = r.json()['content']
        soup = bs(html, 'lxml')
        playerinfo = soup.select_one('.playerinfo')
        row['Name'] = playerinfo.select_one('.name').text
        #row['Team'] = playerinfo.select_one('.player-team-name').text
        row['Position'] = playerinfo.select_one('dd.pos').text[:-1]
        row['Owner'] = playerinfo.select_one('dd.owner').text[:-1]

        # Owner ID
        a = playerinfo.select_one('dd.owner a')
        if a:
            row['Owner ID'] = int(a['href'].split('/')[-1])
        else:
            row['Owner ID'] = np.nan

        # Status
        status = playerinfo.select_one('.status')
        if status:
            row['Status'] = status.text
        else:
            row['Status'] = np.nan

        row['% Owned'] = playerinfo.select_one('dd.owned').text.split()[0]

        # Weekly projections
        df2 = pd.read_html(html)[0]
        for _, row2 in df2.iterrows():
            week = 'Week {}'.format(row2['Week'])
            points = row2['Fan Pts']
            if points[0] == '*':
                # Game hasn't occured yet
                row[week] = float(points[1:])
                #row[week + ' projection'] = float(points[1:])
                #row[week + ' actual'] = np.nan
            elif points == '-':
                # Bye week
                row[week] = 0
                #row[week + ' projection'] = 0
                #row[week + ' actual'] = 0
            else:
                # Game completed
                row[week] = float(points)
                #row[week + ' projection'] = np.nan
                #row[week + ' actual'] = float(points)

        return row
    df = df.apply(get_projections, axis=1)

    # Calculate VOR
    columns = ['Week {}'.format(i) for i in range(current_week(), 18)]
    df['Remaining'] = df[columns].sum(axis=1)
    available = df.loc[df['Owner ID'].isnull()]
    means = available.groupby(['Position'])['Remaining'].nlargest(3).mean(level=0)
    df['VOR'] = df.apply(lambda row: row['Remaining'] - means[row['Position']], axis=1)

    print('Total runtime: {}'.format(datetime.now() - startTime))
    return df


def current_week():
    '''Current season week
    '''

    # Parse current week from a public league
    url = 'https://football.fantasysports.yahoo.com/f1/{}'.format(PUBLIC_LEAGUE)
    r = s.get(url)
    soup = bs(r.text, 'lxml')
    span = soup.select_one('li.Navitem.current a.Navtarget')
    week = span.text.split()[1]
    week = int(week)

    return week
