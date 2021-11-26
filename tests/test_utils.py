import pandas as pd
from pandas.testing import assert_frame_equal

from . import SCRAPER_FILE
import ffbot


def test_load():
    df, week = ffbot.load(SCRAPER_FILE)
    desired_week = 12
    assert week == desired_week
    desired_df = pd.read_csv(SCRAPER_FILE)
    assert_frame_equal(df, desired_df)
