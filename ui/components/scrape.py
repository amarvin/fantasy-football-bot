import dash_bootstrap_components as dbc
import ffbot
from dash import Input, Output, dash_table, html

from app import app

scrape = html.Div(
    [
        html.H1("Scrape"),
        dbc.Row(
            dbc.Col(
                dbc.Button(
                    "1. Scrape",
                    className="me-1",
                    color="primary",
                    id="scrape-scrape-button",
                ),
            ),
        ),
        html.Br(),
        dbc.Row(
            dbc.Col(
                dbc.Button(
                    "2. Load",
                    color="primary",
                    id="scrape-load-button",
                ),
            ),
        ),
        html.Div(
            [
                html.Span("Week "),
                html.Span(id="week"),
            ]
        ),
        dash_table.DataTable(
            id="scrape-table",
            filter_action="native",
            page_action="native",
            page_current=0,
            page_size=10,
            sort_action="native",
            style_as_list_view=True,
            style_table={'overflowX': 'auto'},
        ),
    ]
)


@app.callback(
    Output("week", "children"),
    Output("scrape-table", "columns"),
    Output("scrape-table", "data"),
    Input("scrape-load-button", "n_clicks"),
)
def load(_):
    df, week = ffbot.load()
    columns = [dict(id=i, name=i) for i in df.columns]
    data = df.to_dict("records")
    return week, columns, data
