import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html

from app import app
from components.about import about
from components.body import body
from components.footer import footer
from components.navbar import navbar

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="scrape-source-data"),
        dcc.Store(id="scrape-visible-data"),
        dcc.Store(id="scrape-columns"),
        dcc.Store(id="week-value"),
        dcc.Store(id="optimize-results"),
        navbar,
        html.Main(id="page-content", className="flex-grow-1"),
        footer,
    ],
    className="min-vh-100 d-flex flex-column bg-light",
)


@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
    prevent_initial_call=False,
)
def render_page(pathname):
    if pathname == "/about":
        return about
    if pathname in {"/", None}:
        return body
    return dbc.Container(
        [
            html.H1("Page not found", className="h3 fw-semibold"),
            html.P("That page does not exist.", className="text-secondary"),
            dbc.Button("Back to home", href="/", color="primary"),
        ],
        className="py-5",
    )


if __name__ == "__main__":
    app.run(debug=True)
