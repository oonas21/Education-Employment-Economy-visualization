from dash import html, dcc
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output
from assets.area_colors import area_colors
from assets.country_codes import country_codes
from assets.regions import region_map


def employ_vs_unemploy(app, emp_rate_df, long_term_unemp_df):

    drop_regions = [
        "European Union - 27 countries (from 2020)",
        "Euro area – 20 countries (from 2023)",
        "Euro area - 19 countries  (2015-2022)"
    ]
    emp_rate_df = emp_rate_df.loc[~emp_rate_df["country"].isin(drop_regions)]
    long_term_unemp_df = long_term_unemp_df.loc[~long_term_unemp_df["country"].isin(drop_regions)]

    common_years = sorted(list(set(emp_rate_df['year'].unique()) & set(long_term_unemp_df['year'].unique())))

    # --- Layout ---
    layout = html.Div([
        html.H3("Employment and long-term unemployment correlation", style={
            "fontWeight": "400",
            "textAlign": "center",
            "margin": "2.5rem auto 1.5rem auto",
            "fontSize": "1.5rem",
            "lineHeight": "1.6",
            "maxWidth": "800px",
        }),
        html.H4("See the (negative) correlation between employment rate and long-term unemployment rate", style={
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
                id="employment-corr-year-dropdown",
                options=[{"label": str(y), "value": y} for y in sorted(common_years, reverse=True)],
                value=common_years[-1] if common_years else None,
                clearable=False,
                style={"width": "200px", "marginRight": "20px"}
            ),
            dcc.Dropdown(
                id="region-selector",
                options=[{"label": r, "value": r} for r in ["Select region"] + list(region_map.keys())],
                value="Select region",
                clearable=False,
                style={"width": "250px"}
            ),
        ], style={"display": "flex", "justifyContent": "center", "marginBottom": "20px"}),

        # --- Graph + Sidebar ---
        html.Div([
            dcc.Graph(id="employment-correlation", style={"flex": "4"}),  # bigger chart
            html.Div(id="region-country-list", style={
                "flex": "0.8",  # smaller sidebar
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
        [Output("employment-correlation", "figure"),
         Output("region-country-list", "children")],
        [Input("employment-corr-year-dropdown", "value"),
         Input("region-selector", "value")]
    )
    def update_scatter(selected_year, selected_region):
        if selected_year is None:
            return {}, ""

        # Merge employment and long-term unemployment data
        df_emp = emp_rate_df[emp_rate_df['year'] == selected_year][['country', 'value']]
        df_unemp = long_term_unemp_df[long_term_unemp_df['year'] == selected_year][['country', 'value']]
        df = pd.merge(df_emp, df_unemp, on='country', suffixes=('_emp', '_unemp'))
        df['country_code'] = df['country'].map(country_codes)

        # Base figure: everyone colored by area_colors
        fig = px.scatter(
            df,
            x='value_emp',
            y='value_unemp',
            color='country',
            text='country_code',
            color_discrete_map=area_colors,
            labels={
                'value_emp': 'Employment rate (%)',
                'value_unemp': 'Long-term unemployment rate (%)',
                'country': 'Country'
            },
            title=f"Employment vs. Long-term Unemployment"
        )

        # Default: all visible with normal colors
        fig.update_traces(marker=dict(size=11, opacity=0.9))

        # --- Highlight if a region is selected ---
        if selected_region and selected_region != "Select region":
            highlighted = region_map[selected_region]

            # Reduce opacity for non-selected countries
            fig.for_each_trace(
                lambda trace: trace.update(marker_opacity=0.25)
                if trace.name not in highlighted else trace.update(marker_opacity=1, marker_size=15)
            )

            # Sidebar country list
            countries = region_map[selected_region]
            country_list = [
                html.H5(f"{selected_region}", style={"marginBottom": "10px"})
            ] + [html.Div(f"{country_codes[c]} – {c}") for c in countries]
        else:
            country_list = [html.Div("Select a region to see details.", style={"color": "#9CA3AF"})]

        correlation = df["value_emp"].corr(df["value_unemp"]) ** 2
        fig.update_layout(
            title=f"<br><sup>Correlation: R² = {correlation:.2f}</sup>"
        )
        # Layout tweaks
        fig.update_layout(
            xaxis=dict(range=[df['value_emp'].min() - 2, df['value_emp'].max() + 2]),
            yaxis=dict(range=[df['value_unemp'].min() - 2, df['value_unemp'].max() + 2]),
            height=600,
            hovermode='closest',
            showlegend=False
        )

        return fig, country_list

    return layout
