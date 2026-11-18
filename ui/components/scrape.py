from pathlib import Path

import dash_bootstrap_components as dbc
from app import LEAGUE, app
from dash import Input, Output, State, ctx, dash_table, dcc, html, no_update

import ffbot

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
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Select scraped data")),
                dbc.ModalBody(
                    [
                        html.Div(id="scrape-file-picker-message"),
                        dcc.RadioItems(id="scrape-file-picker-options"),
                    ]
                ),
                dbc.ModalFooter(
                    [
                        dbc.Button(
                            "Cancel", id="scrape-cancel-load", color="secondary"
                        ),
                        dbc.Button(
                            "Load selected",
                            id="scrape-confirm-load",
                            color="primary",
                        ),
                    ]
                ),
            ],
            id="scrape-file-picker",
            is_open=False,
        ),
        dbc.Progress(
            id="scrape-progress",
            value=100,
            label="Scraping…",
            animated=True,
            striped=True,
            style={"display": "none"},
        ),
        html.Div(id="scrape-status"),
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
        dbc.Progress(
            id="load-progress",
            value=100,
            label="Loading…",
            animated=True,
            striped=True,
            style={"display": "none"},
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
            style_table={"overflowX": "auto"},
        ),
    ]
)


@app.callback(
    Output("scrape-file-picker", "is_open"),
    Output("scrape-file-picker-options", "options"),
    Output("scrape-file-picker-options", "value"),
    Output("scrape-file-picker-message", "children"),
    Input("scrape-load-button", "n_clicks"),
    Input("scrape-cancel-load", "n_clicks"),
    Input("scrape-confirm-load", "n_clicks"),
    prevent_initial_call=True,
)
def toggle_file_picker(_, __, ___):
    if ctx.triggered_id == "scrape-load-button":
        files = sorted(
            Path("data").glob("*.csv"),
            key=lambda path: path.stat().st_ctime,
            reverse=True,
        )
        options = [{"label": path.name, "value": str(path)} for path in files]
        selected = options[0]["value"] if options else None
        message = "" if options else "No scraped CSV files were found."
        return True, options, selected, message
    return False, no_update, no_update, no_update


@app.callback(
    Output("scrape-status", "children"),
    Output("week", "children"),
    Output("scrape-table", "columns"),
    Output("scrape-table", "data"),
    Input("scrape-scrape-button", "n_clicks"),
    running=[
        (Output("scrape-progress", "style"), {"display": "block"}, {"display": "none"}),
    ],
    prevent_initial_call=True,
)
def run_scrape(_):
    week = ffbot.current_week()
    df = ffbot.scrape(LEAGUE)
    ffbot.save(df, week)
    columns = [dict(id=column, name=column) for column in df.columns]
    data = df.to_dict("records")
    return (
        f"Scrape complete. Data for week {week} was saved and loaded.",
        week,
        columns,
        data,
    )


@app.callback(
    Output("scrape-status", "children", allow_duplicate=True),
    Output("week", "children", allow_duplicate=True),
    Output("scrape-table", "columns", allow_duplicate=True),
    Output("scrape-table", "data", allow_duplicate=True),
    Input("scrape-confirm-load", "n_clicks"),
    State("scrape-file-picker-options", "value"),
    running=[
        (Output("load-progress", "style"), {"display": "block"}, {"display": "none"})
    ],
    prevent_initial_call=True,
)
def load_selected(_, filepath):
    if not filepath:
        return no_update, no_update, no_update, no_update
    df, week = ffbot.load(filepath)
    columns = [dict(id=column, name=column) for column in df.columns]
    data = df.to_dict("records")
    return f"Loaded {Path(filepath).name}.", week, columns, data
