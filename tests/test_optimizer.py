import pandas as pd

import ffbot

from . import POSITIONS, SCRAPER_FILE, TEAM


def test_optimize():
    df, week = ffbot.load(SCRAPER_FILE)
    assert week == 4
    df_opt = ffbot.optimize(df, week, TEAM, POSITIONS)
    desired_df_opt = """                                Add              Drop Total points Discounted points    VOR
0                                     Player 200 (WR)                                      
1                  <current roster>                        1723.27             420.2  515.9
2                   Player 221 (TE)                           6.11              0.58 -19.01
3                  Player 143 (DEF)   Player 101 (QB)       -10.41              2.33 -16.19
4                    Player 157 (K)    Player 177 (K)         4.06              2.01   4.06
5                  Player 162 (DEF)  Player 140 (DEF)        -1.62              0.64  -5.79
6                    Player 135 (K)    Player 59 (RB)         9.26              0.37 -39.68
7  Player 90 (WR) - Waivers (Jan 2)                           9.45              3.23  17.22
8                                     Player 132 (WR)          0.0               0.0    0.0
9      Player 129 (QB) - Free Agent   Player 174 (WR)        14.53              0.85  11.16"""  # noqa: W291
    assert df_opt.to_string() == desired_df_opt
