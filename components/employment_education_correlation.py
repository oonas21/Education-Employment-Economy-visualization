from dash import html, dcc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
from assets.area_colors import area_colors
from assets.country_codes import country_codes
from assets.regions import region_map


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

        # --- Dropdowns ---
        html.Div([
            dcc.Dropdown(
                id="employment-education-corr-year-dropdown",
                options=[{"label": str(y), "value": y} for y in sorted(years, reverse=True)],
                value=years[-1] if years else None,
                clearable=False,
                style={"width": "200px", "marginRight": "20px"}
            ),
            dcc.Dropdown(
                id="edu-dropdown",
                options=[{"label": name, "value": name} for name in edu_groups.keys()],
                value="Adult education",
                clearable=False,
                style={"width": "250px", "marginRight": "20px"}
            ),
            dcc.Dropdown(
                id="region-selector-edu",
                options=[{"label": r, "value": r} for r in ["Select region"] + list(region_map.keys())],
                value="Select region",
                clearable=False,
                style={"width": "250px"}
            ),
        ], style={"display": "flex", "justifyContent": "center", "marginBottom": "20px"}),

        # --- Two plots + sidebar ---
        html.Div([
            html.Div([
                dcc.Graph(id="employment-education-corr", style={"flex": "1", "minWidth": "400px"}),
                dcc.Graph(id="unemployment-education-corr", style={"flex": "1", "minWidth": "400px"}),
            ], style={"flex": "4", "display": "flex", "flexDirection": "column", "gap": "2%"}),

            html.Div(id="region-country-list-edu", style={
                "flex": "0.8",
                "padding": "10px",
                "borderLeft": "1px solid #ddd",
                "fontSize": "14px",
                "color": "#374151",
                "maxWidth": "220px",
                "overflowY": "auto"
            })
        ], style={"display": "flex", "gap": "2%", "flexWrap": "wrap"})
    ])

    # --- Callback ---
    @app.callback(
        [Output("employment-education-corr", "figure"),
         Output("unemployment-education-corr", "figure"),
         Output("region-country-list-edu", "children")],
        [Input("employment-education-corr-year-dropdown", "value"),
         Input("edu-dropdown", "value"),
         Input("region-selector-edu", "value")]
    )
    def update_scatter(selected_year, selected_edu, selected_region):
        if selected_year is None or selected_edu is None:
            return px.scatter(title="No data available"), px.scatter(title="No data available"), ""

        # Select education dataframe
        edu_df = edu_groups[selected_edu]
        edu_year = edu_df[edu_df["year"] == selected_year][["country", "value"]].rename(columns={"value": "edu_rate"})

        emp_year = emp_rate_df[emp_rate_df["year"] == selected_year][["country", "value"]].rename(columns={"value": "emp_rate"})
        unemp_year = long_term_unemp_df[long_term_unemp_df["year"] == selected_year][["country", "value"]].rename(columns={"value": "unemp_rate"})

        # Merge
        df_emp_corr = pd.merge(emp_year, edu_year, on="country", how="inner")
        df_unemp_corr = pd.merge(unemp_year, edu_year, on="country", how="inner")
        df_emp_corr['country_code'] = df_emp_corr['country'].map(country_codes)
        df_unemp_corr['country_code'] = df_unemp_corr['country'].map(country_codes)

        # Base scatter 1
        fig_emp = px.scatter(
            df_emp_corr,
            x="emp_rate", y="edu_rate", text="country_code",
            color="country", color_discrete_map=area_colors,
            trendline="ols", trendline_color_override="black",
            title=f"{selected_edu} vs Employment Rate ({selected_year})",
            labels={"emp_rate": "Employment rate (%)", "edu_rate": f"{selected_edu} participation rate (%)"},
        )

        # Base scatter 2
        fig_unemp = px.scatter(
            df_unemp_corr,
            x="unemp_rate", y="edu_rate", text="country_code",
            color="country", color_discrete_map=area_colors,
            trendline="ols", trendline_color_override="black",
            title=f"{selected_edu} vs Long-term Unemployment Rate ({selected_year})",
            labels={"unemp_rate": "Long-term unemployment rate (%)", "edu_rate": f"{selected_edu} participation rate (%)"},
        )

        # Default style
        for fig in [fig_emp, fig_unemp]:
            fig.update_traces(marker=dict(size=10, opacity=0.9))
            fig.update_layout(height=550, hovermode="closest", showlegend=False)

        # Highlight selected region
        if selected_region and selected_region != "Select region":
            highlighted = region_map[selected_region]

            for fig in [fig_emp, fig_unemp]:
                fig.for_each_trace(
                    lambda trace: trace.update(marker_opacity=0.25)
                    if trace.name not in highlighted else trace.update(marker_opacity=1, marker_size=14)
                )

            countries = region_map[selected_region]
            country_list = [
                html.H5(f"{selected_region}", style={"marginBottom": "10px"})
            ] + [html.Div(f"{country_codes[c]} – {c}") for c in countries]
        else:
            country_list = [html.Div("Select a region to see details.", style={"color": "#9CA3AF"})]

        # Add R² values
        corr_emp = df_emp_corr["emp_rate"].corr(df_emp_corr["edu_rate"]) ** 2
        corr_unemp = df_unemp_corr["unemp_rate"].corr(df_unemp_corr["edu_rate"]) ** 2
        fig_emp.update_layout(
            title=f"{selected_edu} vs Employment Rate ({selected_year})<br><sup>Correlation: R² = {corr_emp:.2f}</sup>"
        )
        fig_unemp.update_layout(
            title=f"{selected_edu} vs Long-term Unemployment Rate ({selected_year})<br><sup>Correlation: R² = {corr_unemp:.2f}</sup>"
        )

        return fig_emp, fig_unemp, country_list

    return layout
