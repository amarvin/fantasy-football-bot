import pandas as pd
from pandas.testing import assert_frame_equal

import ffbot

from . import SCRAPER_FILE


def test_load():
    df, week = ffbot.load(SCRAPER_FILE)
    desired_week = 4
    assert week == desired_week
    desired_df = pd.read_csv(SCRAPER_FILE)
    assert_frame_equal(df, desired_df)
