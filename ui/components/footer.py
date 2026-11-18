from datetime import date

import dash_bootstrap_components as dbc
from dash import html

footer = html.Footer(
    dbc.Container(
        html.P(f"© {date.today().year} - Alex Marvin"),
        fluid=True,
    )
)
