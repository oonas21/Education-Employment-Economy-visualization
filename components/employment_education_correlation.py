from dash import html, dcc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
from assets.country_colors import country_colors

def employment_education_correlation(app, early_childhood_df, tertiary_df, adult_df, emp_rate_df, long_term_unemp_df):
    
    # Remove EU aggregates
    drop_regions = [
        "European Union - 27 countries (from 2020)",
        "Euro area – 20 countries (from 2023)",
        "Euro area - 19 countries  (2015-2022)"
    ]
    for df in [early_childhood_df, tertiary_df, adult_df, emp_rate_df, long_term_unemp_df]:
        df.drop(df[df["country"].isin(drop_regions)].index, inplace=True)

    # Dropdown options
    years = sorted(list(set(emp_rate_df['year'].unique()) | set(long_term_unemp_df['year'].unique())))
    edu_groups = {
        "Adult education": adult_df,
        "Tertiary education": tertiary_df,
        "Early childhood education": early_childhood_df,
    }

    # Layout
    layout = html.Div([
        html.H3("Correlation: Education vs Employment & Unemployment Rates", 
            style={
                "fontWeight": "400",
                "textAlign": "center",
                "margin": "2.5rem auto 1.5rem auto",
                "fontSize": "1.5rem",
                "lineHeight": "1.6",
                "maxWidth": "800px",
            }),
        
        html.H4("Explore how education participation correlates with employment and long-term unemployment rates across countries.",
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
            id="employment-education-corr-year-dropdown",
            options=[{"label": str(y), "value": y} for y in sorted(years, reverse=True)],
            value=years[-1] if years else None,
            clearable=False,
            style={"width": "250px", "margin": "0 auto 20px auto"}
        ),

        # Education type dropdown
        dcc.Dropdown(
            id="edu-dropdown",
            options=[{"label": name, "value": name} for name in edu_groups.keys()],
            value="Adult education",
            clearable=False,
            style={"width": "250px", "margin": "0 auto 40px auto"}
        ),

        # Two side-by-side scatter plots
        html.Div([
            dcc.Graph(id="employment-education-corr", style={"flex": "1", "minWidth": "400px"}),
        ], style={"display": "flex", "gap": "2%", "flexWrap": "wrap"}),

        html.Div([
            #dcc.Graph(id="employment-education-corr", style={"flex": "1", "minWidth": "400px"}),
            dcc.Graph(id="unemployment-education-corr", style={"flex": "1", "minWidth": "400px"}),
        ], style={"display": "flex", "gap": "2%", "flexWrap": "wrap"})
    ])

    # Callback for both graphs
    @app.callback(
        [Output("employment-education-corr", "figure"),
         Output("unemployment-education-corr", "figure")],
        [Input("employment-education-corr-year-dropdown", "value"),
         Input("edu-dropdown", "value")]
    )
    def update_scatter(selected_year, selected_edu):
        if selected_year is None or selected_edu is None:
            return px.scatter(title="No data available"), px.scatter(title="No data available")

        # Select right education dataframe
        edu_df = edu_groups[selected_edu]
        edu_year = edu_df[edu_df["year"] == selected_year][["country", "value"]].rename(columns={"value": "edu_rate"})

        emp_year = emp_rate_df[emp_rate_df["year"] == selected_year][["country", "value"]].rename(columns={"value": "emp_rate"})
        unemp_year = long_term_unemp_df[long_term_unemp_df["year"] == selected_year][["country", "value"]].rename(columns={"value": "unemp_rate"})

        # Merge to align by country
        df_emp_corr = pd.merge(emp_year, edu_year, on="country", how="inner")
        df_unemp_corr = pd.merge(unemp_year, edu_year, on="country", how="inner")

        # Handle missing data — show empty plots if nothing available
        if df_emp_corr.empty or df_unemp_corr.empty:
            return px.scatter(title=f"No data available for {selected_edu} ({selected_year})"), \
                   px.scatter(title=f"No data available for {selected_edu} ({selected_year})")

        # Scatter 1: Employment rate vs Education
        fig_emp = px.scatter(
            df_emp_corr,
            x="emp_rate",
            y="edu_rate",
            text="country",
            color="country",
            color_discrete_map=country_colors,
            title=f"{selected_edu} vs Employment Rate ({selected_year})",
            labels={"emp_rate": "Employment rate (%)", "edu_rate": f"{selected_edu} participation rate (%)"},
        )
        fig_emp.update_traces(marker=dict(size=10, opacity=0.8), textposition="top center")
        fig_emp.update_layout(height=550, hovermode="closest")

        # Scatter 2: Long-term unemployment rate vs Education
        fig_unemp = px.scatter(
            df_unemp_corr,
            x="unemp_rate",
            y="edu_rate",
            text="country",
            color="country",
            color_discrete_map=country_colors,
            title=f"{selected_edu} vs Long-term Unemployment Rate ({selected_year})",
            labels={"unemp_rate": "Long-term unemployment rate (%)", "edu_rate": f"{selected_edu} participation rate (%)"},
        )
        fig_unemp.update_traces(marker=dict(size=10, opacity=0.8), textposition="top center")
        fig_unemp.update_layout(height=550, hovermode="closest")

        return fig_emp, fig_unemp

    return layout
