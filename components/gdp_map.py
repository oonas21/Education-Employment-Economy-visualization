# components/gdp_maps.py
from dash import html, dcc
import plotly.express as px
from dash.dependencies import Input, Output

def register_gdp_component(app, real_df, investment_df):
    """
    Creates GDP layout and registers callbacks for Dash.
    Returns the layout Div.
    """

    # Find common years
    common_years = sorted(list(set(real_df['year'].unique()) & set(investment_df['year'].unique())))

    # Layout with dropdown + two side-by-side maps
    layout = html.Div([
        html.H2("European GDP Comparison", className="text-2xl font-bold text-center mb-4"),
        html.H3("Real GDP (GDP adjusted for inflation) measures the value of the total final output of goods and services produced by an economy within a certain period of time. \n" \
        "Investment share of GDP indicator measures the share of GDP that is used for investment activities in the government, business and household sectors. " \
        "It's measured as percentage of real GDP of the capita.",
            style={
            "fontSize": "15px",
            "fontWeight": "400",
            "textAlign": "center",
            "margin": "0 auto 1rem auto",
            "marginBottom": "1rem",
            "color": "#4B5563",
            "maxWidth": "800px",  
            "lineHeight": "1.6"  
        }),
        
        dcc.Dropdown(
            id="gdp-year-dropdown",
            options=[{"label": str(y), "value": y} for y in sorted(common_years, reverse=True)],
            value=common_years[-1] if common_years else None,
            clearable=False,
            style={"width": "200px", "margin": "0 auto", "marginBottom": "20px"}
        ),

        html.Div([
            dcc.Graph(id="real-gdp-map", style={"flex": "1", "height": "600px", "minWidth": "400px"}),
            dcc.Graph(id="investment-gdp-map", style={"flex": "1", "height": "600px", "minWidth": "400px"})
        ], style={"display": "flex", "gap": "2%"})
    ], className="my-8")

    # --- Callback to update maps ---
    @app.callback(
        Output("real-gdp-map", "figure"),
        Output("investment-gdp-map", "figure"),
        Input("gdp-year-dropdown", "value")
    )
    def update_gdp_maps(selected_year):
        if selected_year is None:
            return {}, {}

        # Filter data
        real_year = real_df[real_df['year'] == selected_year]
        invest_year = investment_df[investment_df['year'] == selected_year]

        # Real GDP map
        fig_real = px.choropleth(
            real_year,
            locations="country",
            locationmode="country names",
            color="value",
            scope="europe",
            color_continuous_scale="Viridis",
            title=f"Real GDP in euros (€) ({selected_year})"
        )
        fig_real.update_geos(fitbounds="locations")

        # Investment GDP map
        fig_invest = px.choropleth(
            invest_year,
            locations="country",
            locationmode="country names",
            color="value",
            scope="europe",
            color_continuous_scale="Plasma",
            title=f"Investment share of GDP in percentages (%)({selected_year})"
        )
        fig_invest.update_geos(fitbounds="locations")

        return fig_real, fig_invest

    return layout

