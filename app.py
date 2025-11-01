# app.py
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from data_loader import load_all_data
from components import layout_home, gdp_map, gdp_trend, education_map, education_trend, employment_map, employment_trend, employment_vs_unemp, gdp_money, education_people, employment_education_correlation, education_economy_correlation, employment_economy_correlation

app = Dash(__name__, external_stylesheets=["https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"])
server = app.server

dataframes = load_all_data("data")

# Education-related
early_leavers_df = dataframes.get("4_1_early_leavers.csv")
low_achieving_math_df = dataframes.get("4_2_2_low_achieving_math.csv")
low_achieving_df = dataframes.get("4_2_low_achieving.csv")
early_childhood_df = dataframes.get("4_3_early_childhood.csv")
tertiary_educational_df = dataframes.get("4_4_tertiary_educational.csv")
digital_skills_df = dataframes.get("4_5_digital_skills.csv")
adult_learning_df = dataframes.get("4_6_adult_learning.csv")

# Employment/economy-related
employment_rate_df = dataframes.get("8_1_employment_rate.csv")
risk_of_poverty_df = dataframes.get("8_2_risk_of_poverty.csv")
investment_gdp_df = dataframes.get("8_3_investment_gdp.csv")
long_term_unemployment_df = dataframes.get("8_4_long_term_unemployment.csv")
outside_labour_df = dataframes.get("8_5_outside_labour.csv")
real_gdp_df = dataframes.get("8_6_real_gdp.csv")
neet_df = dataframes.get("8_7_neet.csv")

home_component = layout_home.layout
gdp_component = gdp_map.register_gdp_component(app, 
    investment_df=investment_gdp_df,
    real_df=real_gdp_df
)
gdp_trend_component = gdp_trend.gdp_trend_component(app, 
    investment_df=investment_gdp_df,
    real_df=real_gdp_df
)

gdp_money_component = gdp_money.gdp_money_component(app, 
    investment_df=investment_gdp_df,
    real_df=real_gdp_df
)

education_component = education_map.education_component(app,
    early_childhood_df=early_childhood_df,
    tertiary_df=tertiary_educational_df,
    adult_df=adult_learning_df)

education_trend_component = education_trend.education_trend_component(app,
    early_childhood_df=early_childhood_df,
    tertiary_df=tertiary_educational_df,
    adult_df=adult_learning_df)

education_people_component = education_people.education_people_component(app,
    early_childhood_df=early_childhood_df,
    tertiary_df=tertiary_educational_df,
    adult_df=adult_learning_df)


employment_map_component = employment_map.employment_map_component(app, 
    emp_rate_df=employment_rate_df,
    long_term_unemp_df=long_term_unemployment_df)

employment_trend_component = employment_trend.employment_trend_component(app, 
    emp_rate_df=employment_rate_df,
    long_term_unemp_df=long_term_unemployment_df)

employ_vs_unemploy_component = employment_vs_unemp.employ_vs_unemploy(app, 
    emp_rate_df=employment_rate_df,
    long_term_unemp_df=long_term_unemployment_df)

employment_education_corr = employment_education_correlation.employment_education_correlation(app,
    early_childhood_df=early_childhood_df,
    tertiary_df=tertiary_educational_df,
    adult_df=adult_learning_df,
    emp_rate_df=employment_rate_df,
    long_term_unemp_df=long_term_unemployment_df)

economy_education_corr = education_economy_correlation.economy_education_correlation(app,
    early_childhood_df=early_childhood_df,
    tertiary_df=tertiary_educational_df,
    adult_df=adult_learning_df,
    real_df=real_gdp_df,
    investment_df=investment_gdp_df)

economy_employment_corr = employment_economy_correlation.economy_employment_correlation(app,
    emp_rate_df=employment_rate_df,
    long_term_unemp_df=long_term_unemployment_df,
    real_df=real_gdp_df,
    investment_df=investment_gdp_df)

# --- Layout ---
# --- Layout ---
app.layout = html.Div(
    [
        # Home Section
        html.Div(
            home_component,
            style={
                "backgroundColor": "#e5b3e5",
                "padding": "50px 70px",
                "borderRadius": "18px",
                "margin": "40px auto 20px auto",
                "boxShadow": "0 6px 16px rgba(0, 0, 0, 0.1)",
                "maxWidth": "1200px",
            },
        ),

        # --- Two Main Sections ---
        html.Div(
            [
                # Section 1: Basic Indicators
                html.Div(
                    [
                        html.H3(
                            "Basic Indicators",
                            style={
                                "textAlign": "center",
                                "color": "#2c3e50",
                                "marginBottom": "25px",
                                "fontWeight": "600",
                            },
                        ),
                        dbc.Tabs(
                            [
                                dbc.Tab(
                                    html.Div(
                                        [gdp_component, gdp_trend_component, gdp_money_component],
                                        style={"padding": "25px"},
                                    ),
                                    label="GDP",
                                ),
                                dbc.Tab(
                                    html.Div(
                                        [education_component, education_trend_component, education_people_component],
                                        style={"padding": "25px"},
                                    ),
                                    label="Education",
                                ),
                                dbc.Tab(
                                    html.Div(
                                        [employment_map_component, employment_trend_component, employ_vs_unemploy_component],
                                        style={"padding": "25px"},
                                    ),
                                    label="Employment",
                                ),
                            ],
                            id="tabs-basic",
                            active_tab="tab-0",
                            className="mb-3",
                        ),
                    ],
                    style={
                        "backgroundColor": "#f2f5f9",
                        "padding": "40px 60px",
                        "borderRadius": "18px",
                        "margin": "20px auto",
                        "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.1)",
                        "maxWidth": "1200px",
                    },
                ),

                # Section 2: Correlations & Effects
                html.Div(
                    [
                        html.H3(
                            "Correlations Between Sectors",
                            style={
                                "textAlign": "center",
                                "color": "#2c3e50",
                                "marginBottom": "25px",
                                "fontWeight": "600",
                            },
                        ),
                        dbc.Tabs(
                            [
                                dbc.Tab(
                                    html.Div([employment_education_corr], style={"padding": "25px"}),
                                    label="Education ↔ Employment",
                                ),
                                dbc.Tab(
                                    html.Div([economy_education_corr], style={"padding": "25px"}),
                                    label="Education → Economy",
                                ),
                                dbc.Tab(
                                    html.Div([economy_employment_corr], style={"padding": "25px"}),
                                    label="Employment → Economy",
                                ),
                            ],
                            id="tabs-correlations",
                            active_tab="tab-0",
                            className="mb-3",
                        ),
                    ],
                    style={
                        "backgroundColor": "#f2f5f9",
                        "padding": "40px 60px",
                        "borderRadius": "18px",
                        "margin": "20px auto",
                        "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.1)",
                        "maxWidth": "1200px",
                    },
                ),
            ]
        ),

        # Footer
        html.Footer(
            [
                html.Div("© 2025 EU Sustainability Goals Dashboard", 
                        style={"marginBottom": "4px"}),
                html.Div([
                    "Data source: © European Union, Eurostat – ",
                    html.A("https://ec.europa.eu/eurostat", 
                        href="https://ec.europa.eu/eurostat", 
                        target="_blank", 
                        style={"color": "#6c757d", "textDecoration": "none"})
                ], style={"fontSize": "13px", "color": "#6c757d"}),
                html.Div("Data retrieved from Eurostat’s public datasets, processed and visualized by the author.",
                        style={"fontSize": "12px", "color": "#adb5bd", "marginTop": "4px"})
            ],
            className="text-center text-muted py-3",
            style={"marginTop": "50px"},
        ),

    ],
    style={
        "scrollBehavior": "smooth",
        "backgroundColor": "#f8f9fa",
        "fontFamily": "Inter, sans-serif",
    },
)



if __name__ == "__main__":
    app.run(debug=True)


