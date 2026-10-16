import dash_bootstrap_components as dbc
from dash import Dash

LEAGUE = 209760
POSITIONS = "QB, WR, WR, WR, RB, RB, TE, W/R/T, K, DEF, BN, BN, BN, BN, IR"
TEAM = 8

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    prevent_initial_callbacks=True,
    title="ffbot",
)
server = app.server
