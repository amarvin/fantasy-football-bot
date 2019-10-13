from datetime import datetime
from time import sleep

from bs4 import BeautifulSoup as bs
import numpy as np
import requests
import pandas as pd


# A public league for current week and player IDs
LG = 39345


def scrape(lg):
    '''Scrape data

    :param lg: league ID
    '''

    # Start timer
    startTime = datetime.now()

    # Create session
    s = requests.Session()
    s.headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    }

    # Scrape player IDs from a public league
    IDs = set()
    groups = ['QB', 'WR', 'RB', 'TE', 'K', 'DEF']
    for group in groups:
        # Taken players
        i = 0
        while True:
            # Request next 25 best players
            r = s.get(
                'https://football.fantasysports.yahoo.com/f1/{}/players'.format(LG),
                params=dict(
                    count=i * 25,
                    pos=group,
                    status='T',
                ),
            )
            i += 1
            assert r.status_code == 200
            soup = bs(r.text, 'lxml')
            table = soup.select_one('#players-table table')
            rows = table.select('tbody tr')
            if not rows: break
            for row in rows:
                ID = row.select('td')[1].select_one('span.player-status a')['data-ys-playerid']
                IDs.add(ID)

        # Available players (only top 25)
        r = s.get(
            'https://football.fantasysports.yahoo.com/f1/{}/players'.format(LG),
            params=dict(
                pos=group,
                sort='PTS',  # sort by points
                stat1='S_PN4W',  # next 4 weeks (proj)
                status='A',
            ),
        )
        assert r.status_code == 200
        soup = bs(r.text, 'lxml')
        table = soup.select_one('#players-table table')
        rows = table.select('tbody tr')
        for row in rows:
            ID = row.select('td')[1].select_one('span.player-status a')['data-ys-playerid']
            IDs.add(ID)
    
    # Create dataframe
    df = pd.DataFrame(IDs, columns=['ID'])

    # Scrape projections
    def get_projections(row):
        pid = row['ID']
        url = 'https://football.fantasysports.yahoo.com/f1/{}/playernote?pid={}'.format(lg, pid)
        r = s.get(url)
        for _ in range(4):
            if r.status_code == 200: break
            # Retry query
            print('Retrying projections for pid {}'.format(pid))
            sleep(61)
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
            row['Owner ID'] = a['href'].split('/')[-1]
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

    print('Total runtime: {}'.format(datetime.now() - startTime))
    return df


def current_week():
    '''Current season week
    '''

    # Create session
    s = requests.Session()
    s.headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    }

    # Parse current week from a public league
    url = 'https://football.fantasysports.yahoo.com/f1/{}'.format(LG)
    r = s.get(url)
    assert r.status_code == 200
    soup = bs(r.text, 'lxml')
    span = soup.select_one('li.Navitem.current a.Navtarget')
    week = span.text.split()[1]
    week = int(week)

    return week
