from dash import html, dcc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
from assets.country_colors import country_colors

def economy_employment_correlation(app, emp_rate_df, long_term_unemp_df, real_df, investment_df):
    
    # Remove EU aggregates
    drop_regions = [
        "European Union - 27 countries (from 2020)",
        "Euro area – 20 countries (from 2023)",
        "Euro area - 19 countries  (2015-2022)"
    ]
    for df in [emp_rate_df, long_term_unemp_df, real_df, investment_df]:
        df.drop(df[df["country"].isin(drop_regions)].index, inplace=True)

    # Dropdown options
    years = sorted(list(set(real_df['year'].unique()) | set(investment_df['year'].unique())))
    emp_groups = {
        "Employment rate": emp_rate_df,
        "Long-term unemployment rate": long_term_unemp_df,
    }

    # Layout
    layout = html.Div([
        html.H3("Correlation: Employment rate vs GDP & Investment GDP", 
            style={
                "fontWeight": "400",
                "textAlign": "center",
                "margin": "2.5rem auto 1.5rem auto",
                "fontSize": "1.5rem",
                "lineHeight": "1.6",
                "maxWidth": "800px",
            }),
        
        html.H4("Explore how employment rate correlates with GDP and investment GDP across countries.",
            style={
                "fontSize": "15px",
                "fontWeight": "400",
                "textAlign": "center",
                "margin": "0 auto 1rem auto",
                "color": "#4B5563",
                "maxWidth": "800px",  
                "lineHeight": "1.6"  
            }),

        # Year dropdown
        dcc.Dropdown(
            id="economy-employment-corr-year-dropdown",
            options=[{"label": str(y), "value": y} for y in sorted(years, reverse=True)],
            value=years[-1] if years else None,
            clearable=False,
            style={"width": "250px", "margin": "0 auto 20px auto"}
        ),

        # Education type dropdown
        dcc.Dropdown(
            id="employment-dropdown2",
            options=[{"label": name, "value": name} for name in emp_groups.keys()],
            value="Employment rate",
            clearable=False,
            style={"width": "250px", "margin": "0 auto 40px auto"}
        ),

        # Two side-by-side scatter plots
        html.Div([
            dcc.Graph(id="GDP-employment-corr", style={"flex": "1", "minWidth": "400px"}),
        ], style={"display": "flex", "gap": "2%", "flexWrap": "wrap"}),

        html.Div([
            dcc.Graph(id="inv-GDP-employment-corr", style={"flex": "1", "minWidth": "400px"}),
        ], style={"display": "flex", "gap": "2%", "flexWrap": "wrap"})
    ])

    # Callback for both graphs
    @app.callback(
        [Output("GDP-employment-corr", "figure"),
         Output("inv-GDP-employment-corr", "figure")],
        [Input("economy-employment-corr-year-dropdown", "value"),
         Input("employment-dropdown2", "value")]
    )
    def update_scatter(selected_year, selected_emp):
        if selected_year is None or selected_emp is None:
            return px.scatter(title="No data available"), px.scatter(title="No data available")

        # Select right education dataframe
        emp_df = emp_groups[selected_emp]
        emp_year = emp_df[emp_df["year"] == selected_year][["country", "value"]].rename(columns={"value": "emp_rate"})

        real_year = real_df[real_df["year"] == selected_year][["country", "value"]].rename(columns={"value": "GDP_rate"})
        investment_year = investment_df[investment_df["year"] == selected_year][["country", "value"]].rename(columns={"value": "inv_rate"})

        # Merge to align by country
        df_GDP_corr = pd.merge(real_year, emp_year, on="country", how="inner")
        df_inv_corr = pd.merge(investment_year, emp_year, on="country", how="inner")

        # Handle missing data — show empty plots if nothing available
        if df_GDP_corr.empty or df_inv_corr.empty:
            return px.scatter(title=f"No data available for {selected_emp} ({selected_year})"), \
                   px.scatter(title=f"No data available for {selected_emp} ({selected_year})")

        # GDP - selected employment
        fig_gdp = px.scatter(
            df_GDP_corr,
            x="GDP_rate",
            y="emp_rate",
            text="country",
            color="country",
            color_discrete_map=country_colors,
            title=f"{selected_emp} vs GDP ({selected_year})",
            labels={"GDP_rate": "GDP (eur)", "emp_rate": f"{selected_emp} (%)"},
        )
        fig_gdp.update_traces(marker=dict(size=10, opacity=0.8), textposition="top center")
        fig_gdp.update_layout(height=550, hovermode="closest")

        # investment gdp - selected employment
        fig_inv = px.scatter(
            df_inv_corr,
            x="inv_rate",
            y="emp_rate",
            text="country",
            color="country",
            color_discrete_map=country_colors,
            title=f"{selected_emp} vs GDP investment rate ({selected_year})",
            labels={"inv_rate": "GDP investement rate (%)", "emp_rate": f"{selected_emp} (%)"},
        )
        fig_inv.update_traces(marker=dict(size=10, opacity=0.8), textposition="top center")
        fig_inv.update_layout(height=550, hovermode="closest")

        return fig_gdp, fig_inv

    return layout
