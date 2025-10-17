from dash import html, dcc
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output
from assets.country_colors import country_colors

def employ_vs_unemploy(app, emp_rate_df, long_term_unemp_df):


    drop_regions = [
        "European Union - 27 countries (from 2020)",
        "Euro area – 20 countries (from 2023)",
        "Euro area - 19 countries  (2015-2022)"
    ]
    emp_rate_df = emp_rate_df.loc[~emp_rate_df["country"].isin(drop_regions)]
    long_term_unemp_df = long_term_unemp_df.loc[~long_term_unemp_df["country"].isin(drop_regions)]


    common_years = sorted(list(set(emp_rate_df['year'].unique()) & set(long_term_unemp_df['year'].unique())))

    layout = html.Div([
        html.H3("Employment and long-term unemployment correlation", 
            style={
            "fontWeight": "400",          # light-medium weight (like before)
            "textAlign": "center",        # center align
            "margin": "2.5rem auto 1.5rem auto",  # more space on top (≈mt-6)
            "fontSize": "1.5rem",         # same visual size as text-lg / ~24px
            "lineHeight": "1.6",          # balanced vertical spacing
            "maxWidth": "800px",          # keeps it readable
        }),
        html.H4("See the (negative) correlation between employment rate and long-term unemployment rate",
            style={
            "fontSize": "15px",
            "fontWeight": "400",
            "textAlign": "center",
            "margin": "0 auto 1rem auto",
            "marginBottom": "1rem",
            "color": "#4B5563",
            "maxWidth": "800px",  
            "lineHeight": "1.6"  
        }),

        dcc.Dropdown(
            id="employment-year-dropdown",
            options=[{"label": str(y), "value": y} for y in sorted(common_years, reverse=True)],
            value=common_years[-1] if common_years else None,
            clearable=False,
            style={"width": "200px", "margin": "0 auto", "marginBottom": "20px"}
        ),

        html.Div([
            dcc.Graph(id="employment-correlation", style={"flex": "1"}),
        ], style={"display": "flex", "gap": "2%", "flexWrap": "wrap"})
    ])

        # --- Single callback for both graphs ---
    @app.callback(
        Output("employment-correlation", "figure"),
        Input("employment-year-dropdown", "value")
    )
    def update_scatter(selected_year):
        if selected_year is None:
            return {}

        # Merge employment and long-term unemployment data for selected year
        df_emp = emp_rate_df[emp_rate_df['year'] == selected_year][['country', 'value']]
        df_unemp = long_term_unemp_df[long_term_unemp_df['year'] == selected_year][['country', 'value']]
        df = pd.merge(df_emp, df_unemp, on='country', suffixes=('_emp', '_unemp'))

        # Scatter plot
        fig = px.scatter(
            df,
            x='value_emp',
            y='value_unemp',
            color='country',
            text='country',
            color_discrete_map=country_colors,
            labels={'value_emp': 'Employment rate (%)', 'value_unemp': 'Long-term unemployment rate (%)'},
            title=f"Employment vs. Long-term Unemployment ({selected_year})"
        )

        fig.update_traces(marker=dict(size=12), selector=dict(mode='markers'))
        fig.update_layout(
            xaxis=dict(range=[df['value_emp'].min() - 2, df['value_emp'].max() + 2]),
            yaxis=dict(range=[df['value_unemp'].min() - 2, df['value_unemp'].max() + 2]),
            height=600,
            hovermode='closest'
        )

        return fig

    return layout