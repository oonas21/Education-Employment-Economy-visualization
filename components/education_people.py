from dash import html, dcc
from dash.dependencies import Input, Output

import random

def get_emoji(education_type):
    if education_type == "Early childhood education":
        return random.choice(["🧒", "👧"])  # boy or girl
    elif education_type == "Adult education":
        return random.choice(["🧑‍🏫", "👩‍🏫"])  # male or female teacher
    elif education_type == "Tertiary education":
        return "🎓"  # same for all
    else:
        return "📘"  # fallback


def education_people_component(app, early_childhood_df, tertiary_df, adult_df):

    years = sorted(
        list(
            set(early_childhood_df['year'].unique())
            | set(tertiary_df['year'].unique())
            | set(adult_df['year'].unique())
        )
    )

    drop_regions = [
        "European Union - 27 countries (from 2020)",
        "Euro area – 20 countries (from 2023)",
        "Euro area - 19 countries  (2015-2022)"
    ]
    early_childhood_df = early_childhood_df.loc[~early_childhood_df["country"].isin(drop_regions)]
    tertiary_df = tertiary_df.loc[~tertiary_df["country"].isin(drop_regions)]
    adult_df = adult_df.loc[~adult_df["country"].isin(drop_regions)]

    countries = sorted(
        list(
            set(early_childhood_df['country'].unique())
            | set(tertiary_df['country'].unique())
            | set(adult_df['country'].unique())
        )
    )

    layout = html.Div([
        html.H3("Education Comparison", 
            style={
                "fontWeight": "400",
                "textAlign": "center",
                "margin": "2.5rem auto 1.5rem auto",
                "fontSize": "1.5rem",
                "lineHeight": "1.6",
                "maxWidth": "800px",
            }),

        html.H4("Compare number of people with different education levels (each person = 5%)",
            style={
                "fontSize": "15px",
                "fontWeight": "400",
                "textAlign": "center",
                "margin": "0 auto 1rem auto",
                "color": "#4B5563",
                "maxWidth": "800px",
                "lineHeight": "1.6"
            }),

        html.Div("👧 🧒 Early childhood  🎓 Tertiary 👩‍🏫 🧑‍🏫 Adult education",
            style={
                "textAlign": "center",
                "fontSize": "18px",
                "marginBottom": "1rem",
                "color": "#374151"
            }),

        html.Div([
            dcc.Dropdown(
                id="edu-year-dropdown",
                options=[{"label": str(y), "value": y} for y in sorted(years, reverse=True)],
                value=years[-1] if years else None,
                clearable=False,
                style={"width": "200px", "margin": "0 auto 20px auto"}
            ),

            html.Div([
                html.Div([
                    html.Label("Country A", style={"fontWeight": "bold"}),
                    dcc.Dropdown(
                        id="edu-country-a-dropdown",
                        options=[{"label": c, "value": c} for c in countries],
                        value="Finland",
                        clearable=False
                    )
                ], style={"width": "45%"}),

                html.Div([
                    html.Label("Country B", style={"fontWeight": "bold"}),
                    dcc.Dropdown(
                        id="edu-country-b-dropdown",
                        options=[{"label": c, "value": c} for c in countries],
                        value="Sweden",
                        clearable=False
                    )
                ], style={"width": "45%"}),
            ], style={"display": "flex", "justifyContent": "space-between", "gap": "5%"})
        ]),

        html.Div([
            html.Div(id="edu-country-a-visual", className="edu-box"),
            html.Div(id="edu-country-b-visual", className="edu-box")
        ], style={"display": "flex", "justifyContent": "space-around", "gap": "5%", "marginTop": "30px"}),

    ], className="my-8")

    # ---- CALLBACK ----
    @app.callback(
        Output("edu-country-a-visual", "children"),
        Output("edu-country-b-visual", "children"),
        Input("edu-year-dropdown", "value"),
        Input("edu-country-a-dropdown", "value"),
        Input("edu-country-b-dropdown", "value")
    )
    def update_visuals(selected_year, country_a, country_b):
        if not selected_year or not country_a or not country_b:
            return html.Div(), html.Div()

        def num_icons(percentage):
            return min(20, max(0, round(percentage / 5)))  # 1 icon = 5%

        visuals = []
        for country in [country_a, country_b]:
            rows = []

            datasets = [
                ("Early childhood education", early_childhood_df),
                ("Tertiary education", tertiary_df),
                ("Adult education", adult_df)
            ]

            for title, df in datasets:
                row = df[(df['country'] == country) & (df['year'] == selected_year)]
                if row.empty:
                    continue  # skip missing data

                value = float(row.iloc[0]['value'])
                count = num_icons(value)
                icons = []

                for _ in range(count):
                    emoji = get_emoji(title)
                    icons.append(
                        html.Span(
                            emoji,
                            className="edu-person"
                        )
                    )

                rows.append(
                    html.Div([
                        html.Div(title, className="edu-title"),
                        html.Div(icons, className="edu-icon-row")
                    ], className="edu-level-row")
                )

            if not rows:
                visuals.append(
                    html.Div(
                        "No data found for this country and year",
                        className="edu-no-data"
                    )
                )
            else:
                visuals.append(html.Div(rows, className="edu-country-box"))

        return visuals[0], visuals[1]

    return layout
