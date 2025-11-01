from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import os
import math


def gdp_money_component(app, real_df, investment_df):

    # Get all common years
    common_years = sorted(list(set(real_df['year'].unique()) & set(investment_df['year'].unique())))


    countries = sorted(list(set(real_df['country'].unique()) | set(investment_df['country'].unique())))
    # Remove aggregated regions
    for agg in ["European Union - 27 countries (from 2020)",
                "Euro area – 20 countries (from 2023)",
                "Euro area - 19 countries  (2015-2022)"]:
        if agg in countries:
            countries.remove(agg)


    layout = html.Div([
        html.H3("European GDP Comparison", 
            style={
            "fontWeight": "400",          # light-medium weight (like before)
            "textAlign": "center",        # center align
            "margin": "2.5rem auto 1.5rem auto",  # more space on top (≈mt-6)
            "fontSize": "1.5rem",         # same visual size as text-lg / ~24px
            "lineHeight": "1.6",          # balanced vertical spacing
            "maxWidth": "800px",          # keeps it readable
            }),
        html.H4(
            "Compare real GDP (adjusted for inflation) and investment share across countries. "
            "Each money icon represents one thousand euros. Brightened icons show the share of investment.",
            style={
                "fontSize": "15px",
                "fontWeight": "400",
                "textAlign": "center",
                "margin": "0 auto 1rem auto",
                "marginBottom": "1rem",
                "color": "#4B5563",
                "maxWidth": "800px",  
                "lineHeight": "1.6"  
            }
        ),

        # --- Legend for the two money symbols ---
        html.Div(
            style={"display": "flex", "justifyContent": "center", "gap": "20px", "marginBottom": "15px"},
            children=[
                html.Div([
                    html.Span("💰", style={"fontSize": "24px", "marginRight": "5px"}),
                    html.Span("GDP")
                ]),
                html.Div([
                    html.Span("💰", style={"fontSize": "24px", "filter": "brightness(1.8)", "marginRight": "5px"}),
                    html.Span("Investment share")
                ])
            ]
        ),

        html.Div([
            dcc.Dropdown(
                id="gdp-money-year-dropdown",
                options=[{"label": str(y), "value": y} for y in sorted(common_years, reverse=True)],
                value=common_years[-1] if common_years else None,
                clearable=False,
                style={"width": "200px", "margin": "0 auto", "marginBottom": "20px"}
            ),

            html.Div([
                html.Div([
                    html.Label("Country A", style={"fontWeight": "bold"}),
                    dcc.Dropdown(
                        id="country-a-dropdown",
                        options=[{"label": c, "value": c} for c in countries],
                        value="Finland",
                        clearable=False,
                        style={"marginBottom": "20px"}
                    )
                ], style={"width": "45%"}),

                html.Div([
                    html.Label("Country B", style={"fontWeight": "bold"}),
                    dcc.Dropdown(
                        id="country-b-dropdown",
                        options=[{"label": c, "value": c} for c in countries],
                        value="Sweden",
                        clearable=False,
                        style={"marginBottom": "20px"}
                    )
                ], style={"width": "45%"}),
            ], style={"display": "flex", "justifyContent": "space-between", "gap": "5%"})
        ]),

        html.Div([
            html.Div(id="country-a-visual", className="money-grid"),
            html.Div(id="country-b-visual", className="money-grid")
        ], style={"display": "flex", "justifyContent": "space-around", "gap": "5%", "marginTop": "30px"}),
    ], className="my-8")

    # --- Callbacks ---

    @app.callback(
        Output("country-a-visual", "children"),
        Output("country-b-visual", "children"),
        Input("gdp-money-year-dropdown", "value"),
        Input("country-a-dropdown", "value"),
        Input("country-b-dropdown", "value")
    )
    def update_visuals(selected_year, country_a, country_b):
        if not selected_year or not country_a or not country_b:
            return html.Div(), html.Div()

        visuals = []
        for country in [country_a, country_b]:
            # Filter for the right country and year
            real_row = real_df[(real_df['country'] == country) & (real_df['year'] == selected_year)]
            invest_row = investment_df[(investment_df['country'] == country) & (investment_df['year'] == selected_year)]

            if real_row.empty or invest_row.empty:
                visuals.append(
                    html.Div(
                        "No data found")
                )
                continue

            # Both GDP and investment share are stored in the 'value' column
            gdp = float(real_row.iloc[0]['value'])
            invest_share = float(invest_row.iloc[0]['value'])  # e.g. 19.3 (%)

            # Convert GDP to number of icons (each icon = 1000 GDP units)
            total_icons = min(100, max(1, round(gdp / 1000)))
            bright_count = round(total_icons * invest_share / 100)

            # Build emoji icons
            icons = []
            for i in range(total_icons):
                is_bright = i >= total_icons - bright_count  # brighter icons = investment share
                icons.append(
                    html.Span(
                        "💰",  # GDP icon
                        className="money-emoji" if not is_bright else "money-emoji money-bright"
                    )
                )

            visuals.append(list(reversed(icons)))

        return visuals[0], visuals[1]


    return layout
