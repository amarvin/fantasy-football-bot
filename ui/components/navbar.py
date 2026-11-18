import dash_bootstrap_components as dbc
from dash import Input, Output, State, ctx, html

from app import app

navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.NavbarBrand(
                dbc.Stack(
                    [
                        html.Span("ff", className="fw-light"),
                        html.Span("bot", className="fw-bold"),
                    ],
                    direction="horizontal",
                    gap=0,
                ),
                href="/",
            ),
            dbc.NavbarToggler(id="navbar-toggler"),
            dbc.Collapse(
                dbc.Nav(
                    [
                        dbc.NavLink("Home", href="/", active="exact"),
                        dbc.NavLink("About", href="/about", active="exact"),
                    ],
                    className="ms-auto",
                    navbar=True,
                ),
                id="navbar-collapse",
                navbar=True,
                is_open=False,
            ),
        ],
        fluid=False,
    ),
    color="dark",
    dark=True,
    expand="lg",
    className="shadow-sm",
)


@app.callback(
    Output("navbar-collapse", "is_open"),
    Input("navbar-toggler", "n_clicks"),
    Input("url", "pathname"),
    State("navbar-collapse", "is_open"),
    prevent_initial_call=True,
)
def toggle_navbar(_, __, is_open):
    if ctx.triggered_id == "navbar-toggler":
        return not is_open
    return False
