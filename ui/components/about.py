import dash_bootstrap_components as dbc
from dash import html

about = dbc.Container(
    [
        html.P(
            "ABOUT FFBOT",
            className="text-primary fw-semibold small mb-2",
        ),
        html.H1(
            "Make your next roster move with confidence",
            className="display-6 fw-bold mb-3",
        ),
        html.P(
            [
                "ffbot is a Yahoo Fantasy Football assistant that gathers player"
                " projections and helps compare potential roster moves. It brings"
                " player forecasts and value-over-replacement analysis into one simple"
                " workflow."
            ],
            className="lead text-secondary mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H2(
                                    "Collect projections", className="h5 fw-semibold"
                                ),
                                html.P(
                                    "Scrape the current player pool and weekly Yahoo"
                                    " projections.",
                                    className="text-secondary mb-0",
                                ),
                            ]
                        ),
                        className="h-100 border-0 shadow-sm",
                    ),
                    md=4,
                    className="mb-3",
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H2(
                                    "Review the player pool", className="h5 fw-semibold"
                                ),
                                html.P(
                                    "Load a saved CSV, browse the available players,"
                                    " and filter by column values.",
                                    className="text-secondary mb-0",
                                ),
                            ]
                        ),
                        className="h-100 border-0 shadow-sm",
                    ),
                    md=4,
                    className="mb-3",
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H2(
                                    "Compare roster moves", className="h5 fw-semibold"
                                ),
                                html.P(
                                    "Use projected points and value over replacement to"
                                    " evaluate adds and drops.",
                                    className="text-secondary mb-0",
                                ),
                            ]
                        ),
                        className="h-100 border-0 shadow-sm",
                    ),
                    md=4,
                    className="mb-3",
                ),
            ],
            className="g-3",
        ),
    ],
    className="py-4 py-lg-5",
)
