import dash_bootstrap_components as dbc
from dash import html

navbar = dbc.Navbar(
    dbc.Container(
        dbc.NavbarBrand(
            dbc.Stack(
                [
                    html.Span("ff", className="fw-light"),
                    html.Span("bot", className="fw-bold"),
                ],
                direction="horizontal",
                gap=0,
            ),
            href="#",
        ),
        fluid=False,
    ),
    color="dark",
    dark=True,
    className="shadow-sm",
)
