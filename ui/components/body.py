import dash_bootstrap_components as dbc
from dash import Input, Output, State, html

from app import app
from components.optimize import optimize_layout
from components.scrape import scrape_layout

body = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                [
                    html.H1(
                        "Weekly player analysis",
                        className="h3 fw-bold mb-1",
                    ),
                    html.P(
                        "Scrape projections and compare roster moves.",
                        className="text-secondary small mb-0",
                    ),
                ],
                width=12,
            ),
            className="mb-3",
        ),
        dbc.Card(
            [
                dbc.CardHeader(
                    dbc.Tabs(
                        [
                            dbc.Tab(label="1. Scrape & load", tab_id="scrape-tab"),
                            dbc.Tab(label="2. Optimize", tab_id="optimize-tab"),
                        ],
                        id="workflow-tabs",
                        active_tab="scrape-tab",
                    ),
                    className="bg-white border-0 pb-0",
                ),
                dbc.CardBody(html.Div(id="workflow-panel")),
            ],
            className="border-0 shadow-sm",
        ),
    ],
    fluid=False,
    className="py-3 py-lg-4",
)


@app.callback(
    Output("workflow-panel", "children"),
    Input("workflow-tabs", "active_tab"),
    Input("optimize-results", "data"),
    Input("scrape-columns", "data"),
    State("scrape-visible-data", "data"),
    State("week-value", "data"),
    prevent_initial_call=False,
)
def render_workflow(active_tab, optimize_results, scrape_columns, scrape_data, week):
    if active_tab == "optimize-tab":
        return optimize_layout(optimize_results)
    return scrape_layout(scrape_columns, scrape_data, week)
