from dash import html, dcc
import plotly.express as px
from dash.dependencies import Input, Output
from assets.country_colors import country_colors

def employment_trend_component(app, emp_rate_df, long_term_unemp_df):

    # Get list of countries from both datasets
    countries = sorted(list(set(emp_rate_df['country'].unique()) | set(long_term_unemp_df['country'].unique())))
    # Remove aggregated regions
    for agg in ["European Union - 27 countries (from 2020)",
                "Euro area – 20 countries (from 2023)",
                "Euro area - 19 countries  (2015-2022)"]:
        if agg in countries:
            countries.remove(agg)

    layout = html.Div([
        html.H3("Employment and long-term unemployment trends", 
            style={
            "fontWeight": "400",          # light-medium weight (like before)
            "textAlign": "center",        # center align
            "margin": "2.5rem auto 1.5rem auto",  # more space on top (≈mt-6)
            "fontSize": "1.5rem",         # same visual size as text-lg / ~24px
            "lineHeight": "1.6",          # balanced vertical spacing
            "maxWidth": "800px",          # keeps it readable
        }),
        html.H4("Comare employment and long-term unemployment trends between different countries",
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

        # Single dropdown for both graphs
        dcc.Dropdown(
            id="employment-country-dropdown",
            options=[{"label": c, "value": c} for c in countries],
            multi=True,
            value=["Finland"] if countries else None,
            clearable=False,
            style={"width": "300px", "margin": "0 auto", "marginBottom": "10px"}
        ),

        # Graphs side by side (or stacked for smaller screens)
        html.Div([
            dcc.Graph(id="employment-trend", style={"flex": "1", "height": "500px", "width": "800px"}),
            dcc.Graph(id="unemployment-trend", style={"flex": "1", "height": "500px", "width": "800px"})
        ], style={"display": "flex", "gap": "2%", "flexWrap": "wrap"})
    ])

    # --- Single callback for both graphs ---
    @app.callback(
        Output("employment-trend", "figure"),
        Output("unemployment-trend", "figure"),
        Input("employment-country-dropdown", "value")
    )
    def update_gdp_trends(selected_countries):
        if not selected_countries:
            return {}, {}

        # Ensure it’s a list
        if isinstance(selected_countries, str):
            selected_countries = [selected_countries]

        # Filter real GDP
        df_emloyment = emp_rate_df[emp_rate_df['country'].isin(selected_countries)].sort_values("year")
        fig_employment = px.line(
            df_emloyment,
            x="year",
            y="value",
            color="country",
            markers=True,
            title="Employment rate trend",
            labels={"value": "Employment rate (%)", "year": "Year", "country": "Country"},
            color_discrete_map=country_colors
        )
        fig_employment.update_layout(yaxis_title="Employment rate (%)")

        # Filter investment GDP
        df_unemployment = long_term_unemp_df[long_term_unemp_df['country'].isin(selected_countries)].sort_values("year")
        fig_unemployment = px.line(
            df_unemployment,
            x="year",
            y="value",
            color="country",
            markers=True,
            title="Long-term unemployment rate trend",
            labels={"value": "Long-term unemployment rate (%)", "year": "Year", "country": "Country"},
            color_discrete_map=country_colors
        )
        fig_unemployment.update_layout(yaxis_title="Investment GDP (%)")

        return fig_employment, fig_unemployment

    return layout
