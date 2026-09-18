import dash_bootstrap_components as dbc
import pandas as pd
from app import POSITIONS, TEAM, app
from dash import Input, Output, State, dash_table, html
from dash.dash_table.Format import Format, Scheme

import ffbot

optimize = html.Div(
    [
        html.H1("Optimize"),
        dbc.Button(
            "Optimize",
            color="primary",
            id="optimize-button",
        ),
        dash_table.DataTable(
            id="optimize-table",
            fill_width=False,
            filter_action="native",
            page_action="native",
            page_current=0,
            page_size=10,
            sort_action="native",
            style_as_list_view=True,
        ),
    ]
)


@app.callback(
    Output("optimize-table", "columns"),
    Output("optimize-table", "data"),
    Input("optimize-button", "n_clicks"),
    State("scrape-table", "data"),
    State("week", "children"),
)
def run_optimize(_, data, week):
    # Load data
    df = pd.DataFrame(data)
    week = int(week)

    # Run optimizer
    df_opt = ffbot.optimize(df, week, TEAM, POSITIONS)
    columns_opt = [
        (
            dict(id=i, name=i)
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
