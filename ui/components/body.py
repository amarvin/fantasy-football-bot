import dash_bootstrap_components as dbc
from components.optimize import optimize
from components.scrape import scrape

body = dbc.Container(
    [
        scrape,
        optimize,
    ],
    fluid=True,
)
