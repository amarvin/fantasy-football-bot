from app import app
from components.body import body
from components.footer import footer
from components.navbar import navbar
from dash import html

app.layout = html.Div(
    [
        navbar,
        body,
        footer,
    ],
)

if __name__ == "__main__":
    app.run_server(debug=True)
