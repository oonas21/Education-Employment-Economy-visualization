from dash import html, dcc
import plotly.express as px
from dash.dependencies import Input, Output

def gdp_trend_component(app, real_df, investment_df):
    """
    Creates a layout for GDP trend line plots under the maps.
    Registers callbacks to update plots based on selected country.
    Returns the layout Div.
    """

    # Get list of countries from both datasets
    countries = sorted(list(set(real_df['country'].unique()) | set(investment_df['country'].unique())))
    # Remove aggregated regions
    for agg in ["European Union - 27 countries (from 2020)",
                "Euro area – 20 countries (from 2023)",
                "Euro area - 19 countries  (2015-2022)"]:
        if agg in countries:
            countries.remove(agg)

    layout = html.Div([
        html.H3("GDP Trends", className="text-lg font-bold text-center mt-6"),

        # Single dropdown for both graphs
        dcc.Dropdown(
            id="gdp-country-dropdown",
            options=[{"label": c, "value": c} for c in countries],
            multi=True,
            value=["Finland"] if countries else None,
            clearable=False,
            style={"width": "300px", "margin": "0 auto", "marginBottom": "10px"}
        ),

        # Graphs side by side (or stacked for smaller screens)
        html.Div([
            dcc.Graph(id="real-gdp-trend", style={"flex": "1", "height": "400px"}),
            dcc.Graph(id="investment-gdp-trend", style={"flex": "1", "height": "400px"})
        ], style={"display": "flex", "gap": "2%", "flexWrap": "wrap"})
    ])

    # --- Single callback for both graphs ---
    @app.callback(
        Output("real-gdp-trend", "figure"),
        Output("investment-gdp-trend", "figure"),
        Input("gdp-country-dropdown", "value")
    )
    def update_gdp_trends(selected_countries):
        if not selected_countries:
            return {}, {}

        # Ensure it’s a list
        if isinstance(selected_countries, str):
            selected_countries = [selected_countries]

        # Filter real GDP
        df_real = real_df[real_df['country'].isin(selected_countries)].sort_values("year")
        fig_real = px.line(
            df_real,
            x="year",
            y="value",
            color="country",
            markers=True,
            title="Real GDP Trend",
            labels={"value": "GDP (€)", "year": "Year", "country": "Country"}
        )
        fig_real.update_layout(yaxis_title="GDP (€)")

        # Filter investment GDP
        df_invest = investment_df[investment_df['country'].isin(selected_countries)].sort_values("year")
        fig_invest = px.line(
            df_invest,
            x="year",
            y="value",
            color="country",
            markers=True,
            title="Investment GDP Trend",
            labels={"value": "Investment share (%)", "year": "Year", "country": "Country"}
        )
        fig_invest.update_layout(yaxis_title="Investment GDP (%)")

        return fig_real, fig_invest

    return layout
