from dash import html, dcc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
from assets.country_colors import country_colors

def economy_education_correlation(app, early_childhood_df, tertiary_df, adult_df, real_df, investment_df):
    
    # Remove EU aggregates
    drop_regions = [
        "European Union - 27 countries (from 2020)",
        "Euro area – 20 countries (from 2023)",
        "Euro area - 19 countries  (2015-2022)"
    ]
    for df in [early_childhood_df, tertiary_df, adult_df, real_df, investment_df]:
        df.drop(df[df["country"].isin(drop_regions)].index, inplace=True)

    # Dropdown options
    years = sorted(list(set(real_df['year'].unique()) | set(investment_df['year'].unique())))
    edu_groups = {
        "Adult education": adult_df,
        "Tertiary education": tertiary_df,
        "Early childhood education": early_childhood_df,
    }

    # Layout
    layout = html.Div([
        html.H3("Correlation: Education vs GDP & Investment GDP", 
            style={
                "fontWeight": "400",
                "textAlign": "center",
                "margin": "2.5rem auto 1.5rem auto",
                "fontSize": "1.5rem",
                "lineHeight": "1.6",
                "maxWidth": "800px",
            }),
        
        html.H4("Explore how education participation correlates with GDP and investment GDP across countries.",
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
            id="economy-education-corr-year-dropdown",
            options=[{"label": str(y), "value": y} for y in sorted(years, reverse=True)],
            value=years[-1] if years else None,
            clearable=False,
            style={"width": "250px", "margin": "0 auto 20px auto"}
        ),

        # Education type dropdown
        dcc.Dropdown(
            id="edu-dropdown2",
            options=[{"label": name, "value": name} for name in edu_groups.keys()],
            value="Adult education",
            clearable=False,
            style={"width": "250px", "margin": "0 auto 40px auto"}
        ),

        # Two side-by-side scatter plots
        html.Div([
            dcc.Graph(id="GDP-education-corr", style={"flex": "1", "minWidth": "400px"}),
        ], style={"display": "flex", "gap": "2%", "flexWrap": "wrap"}),

        html.Div([
            dcc.Graph(id="inv-GDP-education-corr", style={"flex": "1", "minWidth": "400px"}),
        ], style={"display": "flex", "gap": "2%", "flexWrap": "wrap"})
    ])

    # Callback for both graphs
    @app.callback(
        [Output("GDP-education-corr", "figure"),
         Output("inv-GDP-education-corr", "figure")],
        [Input("economy-education-corr-year-dropdown", "value"),
         Input("edu-dropdown2", "value")]
    )
    def update_scatter(selected_year, selected_edu):
        if selected_year is None or selected_edu is None:
            return px.scatter(title="No data available"), px.scatter(title="No data available")

        # Select right education dataframe
        edu_df = edu_groups[selected_edu]
        edu_year = edu_df[edu_df["year"] == selected_year][["country", "value"]].rename(columns={"value": "edu_rate"})

        real_year = real_df[real_df["year"] == selected_year][["country", "value"]].rename(columns={"value": "GDP_rate"})
        investment_year = investment_df[investment_df["year"] == selected_year][["country", "value"]].rename(columns={"value": "inv_rate"})

        # Merge to align by country
        df_GDP_corr = pd.merge(real_year, edu_year, on="country", how="inner")
        df_inv_corr = pd.merge(investment_year, edu_year, on="country", how="inner")

        # Handle missing data — show empty plots if nothing available
        if df_GDP_corr.empty or df_inv_corr.empty:
            return px.scatter(title=f"No data available for {selected_edu} ({selected_year})"), \
                   px.scatter(title=f"No data available for {selected_edu} ({selected_year})")

        fig_gdp = px.scatter(
            df_GDP_corr,
            x="GDP_rate",
            y="edu_rate",
            text="country",
            color="country",
            color_discrete_map=country_colors,
            title=f"{selected_edu} vs GDP ({selected_year})",
            labels={"GDP_rate": "GDP (eur)", "edu_rate": f"{selected_edu} participation rate (%)"},
        )
        fig_gdp.update_traces(marker=dict(size=10, opacity=0.8), textposition="top center")
        fig_gdp.update_layout(height=550, hovermode="closest")

        # Scatter 2: Long-term unemployment rate vs Education
        fig_inv = px.scatter(
            df_inv_corr,
            x="inv_rate",
            y="edu_rate",
            text="country",
            color="country",
            color_discrete_map=country_colors,
            title=f"{selected_edu} vs GDP investment rate ({selected_year})",
            labels={"inv_rate": "GDP investement rate (%)", "edu_rate": f"{selected_edu} participation rate (%)"},
        )
        fig_inv.update_traces(marker=dict(size=10, opacity=0.8), textposition="top center")
        fig_inv.update_layout(height=550, hovermode="closest")

        # Compute correlation values
        corr_gdp = df_GDP_corr["GDP_rate"].corr(df_GDP_corr["edu_rate"])
        corr_inv = df_inv_corr["inv_rate"].corr(df_inv_corr["edu_rate"])

        # Update titles to show R²
        fig_gdp.update_layout(
            title=f"{selected_edu} vs GDP ({selected_year})<br><sup>Correlation: R² = {corr_gdp**2:.2f}</sup>"
        )
        fig_inv.update_layout(
            title=f"{selected_edu} vs GDP investment rate ({selected_year})<br><sup>Correlation: R² = {corr_inv**2:.2f}</sup>"
        )


        return fig_gdp, fig_inv

    return layout
