from dash import html, dcc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
from assets.area_colors import area_colors
from assets.country_codes import country_codes
from assets.regions import region_map


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

    # --- Layout ---
    layout = html.Div([
        html.H3("Correlation: Employment and Unemployment vs GDP & Investment",
            style={
                "fontWeight": "400",
                "textAlign": "center",
                "margin": "2.5rem auto 1.5rem auto",
                "fontSize": "1.5rem",
                "lineHeight": "1.6",
                "maxWidth": "800px",
            }),
        
        html.H4("Explore how employment and long-term unemployment relate to GDP and investment rates across European countries.",
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
                id="economy-employment-corr-year-dropdown",
                options=[{"label": str(y), "value": y} for y in sorted(years, reverse=True)],
                value=years[-1] if years else None,
                clearable=False,
                style={"width": "200px", "marginRight": "20px"}
            ),
            dcc.Dropdown(
                id="employment-dropdown2",
                options=[{"label": name, "value": name} for name in emp_groups.keys()],
                value="Employment rate",
                clearable=False,
                style={"width": "250px", "marginRight": "20px"}
            ),
            dcc.Dropdown(
                id="region-selector-economy",
                options=[{"label": r, "value": r} for r in ["Select region"] + list(region_map.keys())],
                value="Select region",
                clearable=False,
                style={"width": "250px"}
            ),
        ], style={"display": "flex", "justifyContent": "center", "marginBottom": "20px"}),

        # --- Graphs + Sidebar ---
        html.Div([
            html.Div([
                dcc.Graph(id="GDP-employment-corr", style={"flex": "1", "minWidth": "400px"}),
                dcc.Graph(id="inv-GDP-employment-corr", style={"flex": "1", "minWidth": "400px"}),
            ], style={"flex": "4", "display": "flex", "flexDirection": "column", "gap": "2%"}),

            html.Div(id="region-country-list-economy", style={
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
        [Output("GDP-employment-corr", "figure"),
         Output("inv-GDP-employment-corr", "figure"),
         Output("region-country-list-economy", "children")],
        [Input("economy-employment-corr-year-dropdown", "value"),
         Input("employment-dropdown2", "value"),
         Input("region-selector-economy", "value")]
    )
    def update_scatter(selected_year, selected_emp, selected_region):
        if selected_year is None or selected_emp is None:
            return px.scatter(title="No data available"), px.scatter(title="No data available"), ""

        emp_df = emp_groups[selected_emp]
        emp_year = emp_df[emp_df["year"] == selected_year][["country", "value"]].rename(columns={"value": "emp_rate"})
        real_year = real_df[real_df["year"] == selected_year][["country", "value"]].rename(columns={"value": "GDP_rate"})
        inv_year = investment_df[investment_df["year"] == selected_year][["country", "value"]].rename(columns={"value": "inv_rate"})

        df_GDP_corr = pd.merge(real_year, emp_year, on="country", how="inner")
        df_inv_corr = pd.merge(inv_year, emp_year, on="country", how="inner")
        df_GDP_corr['country_code'] = df_GDP_corr['country'].map(country_codes)
        df_inv_corr['country_code'] = df_inv_corr['country'].map(country_codes)

        # --- GDP vs Employment ---
        fig_gdp = px.scatter(
            df_GDP_corr,
            x="GDP_rate", y="emp_rate", text="country_code",
            color="country", color_discrete_map=area_colors,
            trendline="ols", trendline_color_override="black",
            title=f"{selected_emp} vs GDP ({selected_year})",
            labels={"GDP_rate": "GDP (EUR per capita)", "emp_rate": f"{selected_emp} (%)"},
        )

        # --- Investment vs Employment ---
        fig_inv = px.scatter(
            df_inv_corr,
            x="inv_rate", y="emp_rate", text="country_code",
            color="country", color_discrete_map=area_colors,
            trendline="ols", trendline_color_override="black",
            title=f"{selected_emp} vs Investment in GDP ({selected_year})",
            labels={"inv_rate": "Investment (% of GDP)", "emp_rate": f"{selected_emp} (%)"},
        )

        # Default styling
        for fig in [fig_gdp, fig_inv]:
            fig.update_traces(marker=dict(size=10, opacity=0.9))
            fig.update_layout(height=550, hovermode="closest", showlegend=False)

        # Highlight region
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

        # Compute R² correlations
        corr_gdp = df_GDP_corr["GDP_rate"].corr(df_GDP_corr["emp_rate"]) ** 2
        corr_inv = df_inv_corr["inv_rate"].corr(df_inv_corr["emp_rate"]) ** 2

        fig_gdp.update_layout(
            title=f"{selected_emp} vs GDP ({selected_year})<br><sup>Correlation: R² = {corr_gdp:.2f}</sup>"
        )
        fig_inv.update_layout(
            title=f"{selected_emp} vs Investment in GDP ({selected_year})<br><sup>Correlation: R² = {corr_inv:.2f}</sup>"
        )

        return fig_gdp, fig_inv, country_list

    return layout
