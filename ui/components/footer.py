import dash_bootstrap_components as dbc
from dash import html

footer = html.Footer(
    dbc.Container(
        html.P("© 2021 - Alex Marvin"),
        fluid=True,
    )
)
