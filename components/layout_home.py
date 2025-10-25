# components/layout_home.py
from dash import html, dcc


layout = html.Div(
    [
        html.H1(
            "Education, work and economy in Europe",
            className="display-4 fw-bold text-center mb-3",
        ),
        html.P(
            "Explore effects of quality education and employment rates to economic growth.",
            className="lead text-center text-muted",
        ),
    ],
    className="d-flex flex-column justify-content-center align-items-center",
    style={
        "height": "30vh",  # Makes the section take 60% of viewport height
        "textAlign": "center",
        "padding": "2rem",
    },
)
