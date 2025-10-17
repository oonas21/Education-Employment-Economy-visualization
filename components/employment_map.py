# components/gdp_maps.py
from dash import html, dcc
import plotly.express as px
from dash.dependencies import Input, Output

def employment_map_component(app, emp_rate_df, long_term_unemp_df):
    # Find common years
    common_years = sorted(list(set(emp_rate_df['year'].unique()) & set(long_term_unemp_df['year'].unique())))

    # Layout with dropdown + two side-by-side maps
    layout = html.Div([
        html.H2("Employment and long term unemployment rates", className="text-2xl font-bold text-center mb-4"),
        html.H3("Employment rate measures the share of the population aged 20 to 64 which is employed. " \
        "Long-term unemployment rate measures the share of the economically active population aged 15 to 74 who has been unemployed for 12 months or more.",
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
            id="employment-year-dropdown",
            options=[{"label": str(y), "value": y} for y in sorted(common_years, reverse=True)],
            value=common_years[-1] if common_years else None,
            clearable=False,
            style={"width": "200px", "margin": "0 auto", "marginBottom": "20px"}
        ),

        html.Div([
            dcc.Graph(id="employment-map", style={"flex": "1", "height": "600px", "minWidth": "400px"}),
            dcc.Graph(id="unemployment-map", style={"flex": "1", "height": "600px", "minWidth": "400px"}),
        ], style={"display": "flex", "gap": "2%"})
    ], className="my-8")

    # --- Callback to update maps ---
    @app.callback(
        Output("employment-map", "figure"),
        Output("unemployment-map", "figure"),
        Input("employment-year-dropdown", "value")
    )
    def update_education_maps(selected_year):
        if selected_year is None:
            return {}, {}

        # Filter data
        emp_year = emp_rate_df[emp_rate_df['year'] == selected_year]
        unemp_year = long_term_unemp_df[long_term_unemp_df['year'] == selected_year]

        # Employment map
        fig_employment = px.choropleth(
            emp_year,
            locations="country",
            locationmode="country names",
            color="value",
            scope="europe",
            color_continuous_scale="Viridis",
            title=f"Employment rate (%)"
        )
        fig_employment.update_geos(fitbounds="locations")

        # Unemployment map
        fig_unemployment = px.choropleth(
            unemp_year,
            locations="country",
            locationmode="country names",
            color="value",
            scope="europe",
            color_continuous_scale="Plasma",
            title=f"Long-term unemployment rate (%)"
        )
        fig_unemployment.update_geos(fitbounds="locations")

        return  fig_employment, fig_unemployment
    return layout
