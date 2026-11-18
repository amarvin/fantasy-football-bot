import dash_bootstrap_components as dbc
import pandas as pd
from app import POSITIONS, TEAM, app
from dash import Input, Output, State, dash_table, html
from dash.dash_table.Format import Format, Scheme

import ffbot

optimize = html.Div(
    [
        html.H2("2. Optimize roster", className="h4 fw-semibold mb-3"),
        dbc.Button(
            "Find best moves",
            color="primary",
            id="optimize-button",
        ),
        dbc.Progress(
            id="optimize-progress",
            value=100,
            label="Optimizing…",
            animated=True,
            striped=True,
            style={"display": "none"},
        ),
        dash_table.DataTable(
            id="optimize-table",
            fill_width=False,
            filter_action="none",
            page_action="native",
            page_current=0,
            page_size=10,
            sort_action="none",
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
    Output("optimize-table", "columns"),
    Output("optimize-table", "data"),
    Input("optimize-button", "n_clicks"),
    State("scrape-table", "data"),
    State("week", "children"),
    running=[
        (
            Output("optimize-progress", "style"),
            {"display": "block"},
            {"display": "none"},
        )
    ],
)
def run_optimize(_, data, week):
    # Load data
    df = pd.DataFrame(data)
    week = int(week)

    # Run optimizer
    df_opt = ffbot.optimize(df, week, TEAM, POSITIONS)
    columns_opt = [
        (
            dict(id=i, name=i, type="text")
            if i in ["Add", "Drop"]
            else dict(
                format=Format(precision=2, scheme=Scheme.fixed),
                id=i,
                name=i,
                type="numeric",
            )
        )
        for i in df_opt.columns
    ]
    data_opt = df_opt.to_dict("records")
    return columns_opt, data_opt
