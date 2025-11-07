from dash import html, dcc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
from assets.area_colors import area_colors
from assets.country_codes import country_codes
from assets.regions import region_map


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

    # --- Layout ---
    layout = html.Div([
        html.H3("Correlation: Education vs GDP & Investment",
            style={
                "fontWeight": "400",
                "textAlign": "center",
                "margin": "2.5rem auto 1.5rem auto",
                "fontSize": "1.5rem",
                "lineHeight": "1.6",
                "maxWidth": "800px",
            }),
        
        html.H4("Explore how education participation relates to GDP and investment levels across European countries.",
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
                id="economy-education-corr-year-dropdown",
                options=[{"label": str(y), "value": y} for y in sorted(years, reverse=True)],
                value=years[-1] if years else None,
                clearable=False,
                style={"width": "200px", "marginRight": "20px"}
            ),
            dcc.Dropdown(
                id="edu-dropdown2",
                options=[{"label": name, "value": name} for name in edu_groups.keys()],
                value="Adult education",
                clearable=False,
                style={"width": "250px", "marginRight": "20px"}
            ),
            dcc.Dropdown(
                id="region-selector-education",
                options=[{"label": r, "value": r} for r in ["Select region"] + list(region_map.keys())],
                value="Select region",
                clearable=False,
                style={"width": "250px"}
            ),
        ], style={"display": "flex", "justifyContent": "center", "marginBottom": "20px"}),

        # --- Graphs + Sidebar ---
        html.Div([
            html.Div([
                dcc.Graph(id="GDP-education-corr", style={"flex": "1", "minWidth": "400px"}),
                dcc.Graph(id="inv-GDP-education-corr", style={"flex": "1", "minWidth": "400px"}),
            ], style={"flex": "4", "display": "flex", "flexDirection": "column", "gap": "2%"}),

            html.Div(id="region-country-list-education", style={
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
        [Output("GDP-education-corr", "figure"),
         Output("inv-GDP-education-corr", "figure"),
         Output("region-country-list-education", "children")],
        [Input("economy-education-corr-year-dropdown", "value"),
         Input("edu-dropdown2", "value"),
         Input("region-selector-education", "value")]
    )
    def update_scatter(selected_year, selected_edu, selected_region):
        if selected_year is None or selected_edu is None:
            return px.scatter(title="No data available"), px.scatter(title="No data available"), ""

        edu_df = edu_groups[selected_edu]
        edu_year = edu_df[edu_df["year"] == selected_year][["country", "value"]].rename(columns={"value": "edu_rate"})
        real_year = real_df[real_df["year"] == selected_year][["country", "value"]].rename(columns={"value": "GDP_rate"})
        inv_year = investment_df[investment_df["year"] == selected_year][["country", "value"]].rename(columns={"value": "inv_rate"})

        # Merge data
        df_GDP_corr = pd.merge(real_year, edu_year, on="country", how="inner")
        df_inv_corr = pd.merge(inv_year, edu_year, on="country", how="inner")
        df_GDP_corr['country_code'] = df_GDP_corr['country'].map(country_codes)
        df_inv_corr['country_code'] = df_inv_corr['country'].map(country_codes)

        # --- GDP vs Education ---
        fig_gdp = px.scatter(
            df_GDP_corr,
            x="GDP_rate", y="edu_rate", text="country_code",
            color="country", color_discrete_map=area_colors,
            trendline="ols", trendline_color_override="black",
            title=f"{selected_edu} vs GDP ({selected_year})",
            labels={"GDP_rate": "GDP (EUR per capita)", "edu_rate": f"{selected_edu} participation (%)"},
        )

        # --- Investment vs Education ---
        fig_inv = px.scatter(
            df_inv_corr,
            x="inv_rate", y="edu_rate", text="country_code",
            color="country", color_discrete_map=area_colors,
            trendline="ols", trendline_color_override="black",
            title=f"{selected_edu} vs Investment in GDP ({selected_year})",
            labels={"inv_rate": "Investment (% of GDP)", "edu_rate": f"{selected_edu} participation (%)"},
        )

        # Default styling
        for fig in [fig_gdp, fig_inv]:
            fig.update_traces(marker=dict(size=10, opacity=0.9))
            fig.update_layout(height=550, hovermode="closest", showlegend=False)

        # Highlight selected region
        if selected_region and selected_region != "Select region":
            highlighted = region_map[selected_region]

            for fig in [fig_gdp, fig_inv]:
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

        # --- Correlations (R²) ---
        corr_gdp = df_GDP_corr["GDP_rate"].corr(df_GDP_corr["edu_rate"]) ** 2
        corr_inv = df_inv_corr["inv_rate"].corr(df_inv_corr["edu_rate"]) ** 2

        fig_gdp.update_layout(
            title=f"{selected_edu} vs GDP ({selected_year})<br><sup>Coefficient of determination of all datapoints: R² = {corr_gdp:.2f}</sup>"
        )
        fig_inv.update_layout(
            title=f"{selected_edu} vs Investment in GDP ({selected_year})<br><sup>Coefficient of determination of all datapoints: R² = {corr_inv:.2f}</sup>"
        )

        return fig_gdp, fig_inv, country_list

    return layout
