from pathlib import Path

import dash_bootstrap_components as dbc
from app import LEAGUE, app
from dash import Input, Output, State, ctx, dash_table, dcc, html, no_update
from pandas.api.types import is_string_dtype

import ffbot

scrape = html.Div(
    [
        html.H2("1. Scrape player data", className="h4 fw-semibold mb-3"),
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
        html.Div(id="scrape-status", className="small text-secondary mt-2"),
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
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label("Column", className="small fw-semibold"),
                        dcc.Dropdown(
                            id="scrape-filter-column",
                            placeholder="Select a column",
                            clearable=False,
                        ),
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        dbc.Label("Values", className="small fw-semibold"),
                        dcc.Dropdown(
                            id="scrape-filter-values",
                            placeholder="Select one or more values",
                            multi=True,
                        ),
                    ],
                    md=8,
                ),
            ],
            id="scrape-filter-controls",
            className="mb-3",
            style={"display": "none"},
        ),
        dcc.Store(id="scrape-source-data"),
        html.Div(
            [
                html.Span("Loaded data · Week "),
                dbc.Badge(id="week", color="secondary", className="ms-1"),
            ],
            className="small text-secondary mb-2",
        ),
        dash_table.DataTable(
            id="scrape-table",
            filter_action="none",
            page_action="native",
            page_current=0,
            page_size=10,
            sort_action="native",
            style_as_list_view=True,
            style_data_conditional=[
                {"if": {"column_type": "text"}, "textAlign": "left"},
                {"if": {"row_index": "odd"}, "backgroundColor": "#f8fafc"},
            ],
            style_header_conditional=[
                {"if": {"column_type": "text"}, "textAlign": "left"}
            ],
            style_table={"overflowX": "auto"},
            style_cell={
                "fontFamily": "system-ui, -apple-system, Segoe UI, sans-serif",
                "fontSize": "0.9rem",
                "padding": "0.7rem 0.85rem",
                "minWidth": "7rem",
            },
            style_header={
                "backgroundColor": "#f1f5f9",
                "color": "#334155",
                "fontWeight": "600",
                "borderBottom": "1px solid #cbd5e1",
            },
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
    Output("scrape-source-data", "data"),
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
    columns = [
        dict(
            id=column,
            name=column,
            **({"type": "text"} if is_string_dtype(df[column]) else {}),
        )
        for column in df.columns
        if column not in {"ID", "Owner ID"}
    ]
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
    Output("scrape-source-data", "data", allow_duplicate=True),
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
    columns = [
        dict(
            id=column,
            name=column,
            **({"type": "text"} if is_string_dtype(df[column]) else {}),
        )
        for column in df.columns
        if column not in {"ID", "Owner ID"}
    ]
    data = df.to_dict("records")
    return f"Loaded {Path(filepath).name}.", week, columns, data


@app.callback(
    Output("scrape-filter-controls", "style"),
    Input("scrape-source-data", "data"),
)
def toggle_filter_controls(data):
    return {"display": "block"} if data else {"display": "none"}


@app.callback(
    Output("scrape-filter-column", "options"),
    Output("scrape-filter-column", "value"),
    Input("scrape-source-data", "data"),
    State("scrape-filter-column", "value"),
)
def populate_filter_columns(data, selected_column):
    columns = (
        [column for column in data[0] if column not in {"ID", "Owner ID"}]
        if data
        else []
    )
    options = [{"label": column, "value": column} for column in columns]
    if selected_column not in columns:
        selected_column = columns[0] if columns else None
    return options, selected_column


@app.callback(
    Output("scrape-filter-values", "options"),
    Output("scrape-filter-values", "value"),
    Input("scrape-filter-column", "value"),
    State("scrape-source-data", "data"),
)
def populate_filter_values(column, data):
    if not column or not data:
        return [], []
    values = sorted(
        {str(row[column]) for row in data if row.get(column) is not None},
        key=str.casefold,
    )
    options = [{"label": value, "value": value} for value in values]
    return options, []


@app.callback(
    Output("scrape-table", "data"),
    Input("scrape-source-data", "data"),
    Input("scrape-filter-column", "value"),
    Input("scrape-filter-values", "value"),
)
def filter_table(data, column, selected_values):
    if not data:
        return []
    if not column or not selected_values:
        return data
    selected_values = set(selected_values)
    return [row for row in data if str(row.get(column)) in selected_values]
