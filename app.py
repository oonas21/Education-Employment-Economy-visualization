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
app.layout = html.Div(
    [
        # Home Section (always visible)
        html.Div(
            [home_component],
            style={
                "backgroundColor": "#e5b3e5",
                "padding": "40px 60px",
                "borderRadius": "16px",
                "margin": "30px auto",
                "boxShadow": "0 4px 10px rgba(0, 0, 0, 0.1)",
                "maxWidth": "1400px"
            },
        ),

        # --- Accordion for all “basic” visualizations ---
        html.Div(
            dbc.Accordion(
                [
                    # Outer Accordion Item
                    dbc.AccordionItem(
                        [
                            # Inner Accordion for subcategories
                            dbc.Accordion(
                                [
                                    # GDP Sub-Accordion
                                    dbc.AccordionItem(
                                        [
                                            html.Div(
                                                [gdp_component, gdp_trend_component, gdp_money_component],
                                                style={
                                                    "backgroundColor": "#e6eef4",
                                                    "padding": "40px 60px",
                                                    "borderRadius": "16px",
                                                    "margin": "30px auto",
                                                    "boxShadow": "0 4px 10px rgba(0, 0, 0, 0.1)",
                                                    "maxWidth": "1400px"
                                                },
                                            ),
                                        ],
                                        title="💶 GDP Indicators",
                                    ),

                                    # Education Sub-Accordion
                                    dbc.AccordionItem(
                                        [
                                            html.Div(
                                                [education_component, education_trend_component, education_people_component],
                                                style={
                                                    "backgroundColor": "#e6eef4",
                                                    "padding": "40px 60px",
                                                    "borderRadius": "16px",
                                                    "margin": "30px auto",
                                                    "boxShadow": "0 4px 10px rgba(0, 0, 0, 0.1)",
                                                    "maxWidth": "1400px"
                                                },
                                            ),
                                        ],
                                        title="🎓 Education Indicators",
                                    ),

                                    # Employment Sub-Accordion
                                    dbc.AccordionItem(
                                        [
                                            html.Div(
                                                [employment_map_component, employment_trend_component, employ_vs_unemploy_component],
                                                style={
                                                    "backgroundColor": "#e6eef4",
                                                    "padding": "40px 60px",
                                                    "borderRadius": "16px",
                                                    "margin": "30px auto",
                                                    "boxShadow": "0 4px 10px rgba(0, 0, 0, 0.1)",
                                                    "maxWidth": "1400px"
                                                },
                                            ),
                                        ],
                                        title="💼 Employment Indicators",
                                    ),
                                ],
                                always_open=True,
                                start_collapsed=True,
                            )
                        ],
                        title=html.H4(
                            "📊 Basic Indicators",
                            style={
                                "display": "flex",
                                "justifyContent": "center",
                                "alignItems": "center",
                                "fontWeight": "600",
                                "fontSize": "1.6rem",
                                "width": "100%",
                                "color": "#2c3e50",
                                "margin": "0 auto"
                            },
                        ),
                    ),
                    dbc.AccordionItem(
                       [
                            # Inner Accordion for subcategories
                            dbc.Accordion(
                                [
                                    # education - employment
                                    dbc.AccordionItem(
                                        [
                                            html.Div(
                                                [employment_education_corr],
                                                style={
                                                    "backgroundColor": "#e6eef4",
                                                    "padding": "40px 60px",
                                                    "borderRadius": "16px",
                                                    "margin": "30px auto",
                                                    "boxShadow": "0 4px 10px rgba(0, 0, 0, 0.1)",
                                                    "maxWidth": "1400px"
                                                },
                                            ),
                                        ],
                                        title="Connections between education on employment",
                                    ),

                                    # education - economy
                                    dbc.AccordionItem(
                                        [
                                            html.Div(
                                                [economy_education_corr],
                                                style={
                                                    "backgroundColor": "#e6eef4",
                                                    "padding": "40px 60px",
                                                    "borderRadius": "16px",
                                                    "margin": "30px auto",
                                                    "boxShadow": "0 4px 10px rgba(0, 0, 0, 0.1)",
                                                    "maxWidth": "1400px"
                                                },
                                            ),
                                        ],
                                        title="Effects of education to economy",
                                    ),

                                    # employment - economy
                                    dbc.AccordionItem(
                                        [
                                            html.Div(
                                                [economy_employment_corr],
                                                style={
                                                    "backgroundColor": "#e6eef4",
                                                    "padding": "40px 60px",
                                                    "borderRadius": "16px",
                                                    "margin": "30px auto",
                                                    "boxShadow": "0 4px 10px rgba(0, 0, 0, 0.1)",
                                                    "maxWidth": "1400px"
                                                },
                                            ),
                                        ],
                                        title="Effects of employment rates to economy",
                                    ),
                                    # summary
                                    dbc.AccordionItem(
                                        [
                                            html.Div(
                                                [],
                                                style={
                                                    "backgroundColor": "#e6eef4",
                                                    "padding": "40px 60px",
                                                    "borderRadius": "16px",
                                                    "margin": "30px auto",
                                                    "boxShadow": "0 4px 10px rgba(0, 0, 0, 0.1)",
                                                    "maxWidth": "1400px"
                                                },
                                            ),
                                        ],
                                        title="Summary of the effects",
                                    ),
                                ],
                                always_open=True,
                                start_collapsed=True,
                            )
                        ],
                        title=html.H4(
                            "Effects of education and employment rates on economy",
                            style={
                                "display": "flex",
                                "justifyContent": "center",
                                "alignItems": "center",
                                "fontWeight": "600",
                                "fontSize": "1.6rem",
                                "width": "100%",
                                "color": "#2c3e50",
                                "margin": "0 auto"
                            },
                        ),

                    ),
                ],
                always_open=True,
                start_collapsed=True,
                className="my-4 w-100",
            ),
            style={
                "maxWidth": "1400px",
                "margin": "0 auto",
                "borderRadius": "12px",
                "boxShadow": "0 4px 10px rgba(0,0,0,0.1)",
            },
        ),

        # Footer
        html.Footer(
            "© 2025 EU Sustainability Goals",
            className="text-center text-muted py-3",
            style={"marginTop": "40px"}
        ),
    ],
    style={"scrollBehavior": "smooth", "backgroundColor": "#f8f9fa"},
)



if __name__ == "__main__":
    app.run(debug=True)


