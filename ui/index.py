from app import app
from components.body import body
from components.footer import footer
from components.navbar import navbar
from dash import html

app.layout = html.Div(
    [
        navbar,
        html.Main(body, className="flex-grow-1"),
        footer,
    ],
    className="min-vh-100 d-flex flex-column bg-light",
)

if __name__ == "__main__":
    app.run(debug=True)
