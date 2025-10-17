# components/gdp_maps.py
from dash import html, dcc
import plotly.express as px
from dash.dependencies import Input, Output

def education_component(app, early_childhood_df, tertiary_df, adult_df):
    # Find common years
    common_years = sorted(list(set(early_childhood_df['year'].unique()) & set(tertiary_df['year'].unique()) & set(adult_df['year'].unique())))

    # Layout with dropdown + two side-by-side maps
    layout = html.Div([
        html.H2("Education in different ages", className="text-2xl font-bold text-center mb-4"),
        html.H3("Partipication in early childhood education measures the share of the children between the age of three and the starting age of compulsory primary education who participated in early childhood education and care. " \
        "Persons aged 25-34 with tertiary educational attainment level measures the share of the population aged 25-34 who have successfully completed tertiary studies. " \
        "Adult participation in learning measures the share of people aged 25 to 64 who stated that they received formal or non-formal education and training in the four weeks preceding the survey",
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
            id="education-year-dropdown",
            options=[{"label": str(y), "value": y} for y in sorted(common_years, reverse=True)],
            value=common_years[-1] if common_years else None,
            clearable=False,
            style={"width": "200px", "margin": "0 auto", "marginBottom": "20px"}
        ),

        html.Div([
            dcc.Graph(id="early-childhood-map", style={"flex": "1"}),
            dcc.Graph(id="tertiary-map", style={"flex": "1"}),
            dcc.Graph(id="adulthood-map", style={"flex": "1"})
        ], style={
            "display": "flex",
            "gap": "1%",   # optional — reduce spacing
            "width": "100%",
        })
    ], className="my-8")

    # --- Callback to update maps ---
    @app.callback(
        Output("early-childhood-map", "figure"),
        Output("tertiary-map", "figure"),
        Output("adulthood-map", "figure"),
        Input("education-year-dropdown", "value")
    )
    def update_education_maps(selected_year):
        if selected_year is None:
            return {}, {}, {}

        # Filter data
        childhood_year = early_childhood_df[early_childhood_df['year'] == selected_year]
        tertiary_year = tertiary_df[tertiary_df['year'] == selected_year]
        adulthood_year = adult_df[adult_df['year'] == selected_year]

        # Early childhood map
        fig_childhood = px.choropleth(
            childhood_year,
            locations="country",
            locationmode="country names",
            color="value",
            scope="europe",
            color_continuous_scale="Viridis",
            title=f"Participation in early childhood education (%)"
        )
        fig_childhood.update_geos(fitbounds="locations")
        fig_childhood.update_layout(
            coloraxis_colorbar=dict(
                thickness=10,
                len=1
            )
        )

        # Tertiary map
        fig_tertiary = px.choropleth(
            tertiary_year,
            locations="country",
            locationmode="country names",
            color="value",
            scope="europe",
            color_continuous_scale="Plasma",
            title=f"Persons aged 25-34 with tertiary education (%)"
        )
        fig_tertiary.update_geos(fitbounds="locations")
        fig_tertiary.update_layout(
            coloraxis_colorbar=dict(
                thickness=10,
                len=1
            )
        )

        # Adulthood map
        fig_adulthood = px.choropleth(
            adulthood_year,
            locations="country",
            locationmode="country names",
            color="value",
            scope="europe",
            color_continuous_scale="Plasma",
            title=f"Adult participation in learning (%)"
        )
        fig_adulthood.update_geos(fitbounds="locations")
        fig_adulthood.update_layout(
            coloraxis_colorbar=dict(
                thickness=10,
                len=1
            )
        )

        return  fig_childhood, fig_tertiary, fig_adulthood

    return layout
