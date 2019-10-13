from datetime import datetime
from os import listdir, makedirs
from os.path import exists, getctime, isfile, join, split
import re

import pandas as pd


def save(df, week):
    '''Save scraped data
    '''

    # Create data folder, if it doesn't exist
    folder = 'data'
    if not exists(folder):
        makedirs(folder)

    # Create filename
    startTime = datetime.now()
    filename = join(folder, '{:%Y-%m-%d %H%M} week {}.csv'.format(startTime, week))

    # Save data
    df.to_csv(filename, index=False)


def load():
    '''Load latest scraped data
    '''

    # Find latest csv file
    folder = join('.', 'data')
    files = [f for f in listdir(folder) if isfile(join(folder, f))]
    latest_file = max([join(folder, f) for f in files], key=getctime)
    latest_filename = split(latest_file)[1]

    # Unpack data
    week = re.findall(r'\d+', latest_filename)[-1]
    week = int(week)
    df = pd.read_csv(latest_file)

    # Return results
    return df, week
