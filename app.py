# app.py
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from data_loader import load_all_data
from components import layout_home, gdp_map, gdp_trend, education_map, education_trend

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

education_component = education_map.education_component(app,
    early_childhood_df=early_childhood_df,
    tertiary_df=tertiary_educational_df,
    adult_df=adult_learning_df)

education_trend_component = education_trend.education_trend_component(app,
    early_childhood_df=early_childhood_df,
    tertiary_df=tertiary_educational_df,
    adult_df=adult_learning_df)


app.layout = html.Div(
    [
    home_component,
    gdp_component,
    gdp_trend_component,
    education_component,
    education_trend_component,
    html.Footer("© 2025 EU Dashboard Project", className="text-center text-muted py-3")
], style={"scrollBehavior": "smooth"})

if __name__ == "__main__":
    app.run(debug=True)
