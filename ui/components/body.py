import dash_bootstrap_components as dbc
from dash import html

from components.optimize import optimize
from components.scrape import scrape

body = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                [
                    html.P(
                        "FANTASY FOOTBALL TOOLS",
                        className="text-primary fw-semibold small mb-2",
                    ),
                    html.H1(
                        "Weekly player analysis",
                        className="display-6 fw-bold mb-2",
                    ),
                    html.P(
                        "Refresh projections, review player data, and compare roster moves.",
                        className="text-secondary mb-0",
                    ),
                ],
                width=12,
            ),
            className="mb-4 mb-lg-5",
        ),
        dbc.Row(
            dbc.Col(
                dbc.Card(dbc.CardBody(scrape), className="border-0 shadow-sm"),
                width=12,
            ),
            className="mb-4",
        ),
        dbc.Row(
            dbc.Col(
                dbc.Card(dbc.CardBody(optimize), className="border-0 shadow-sm"),
                width=12,
            ),
        ),
    ],
    fluid=False,
    className="py-4 py-lg-5",
)
