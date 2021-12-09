from dash import html

from app import app
from components.body import body
from components.footer import footer
from components.navbar import navbar

app.layout = html.Div(
    [
        navbar,
        body,
        footer,
    ],
)

if __name__ == "__main__":
    app.run_server(debug=True)
