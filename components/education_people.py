from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd


def education_people_component(app, early_childhood_df, tertiary_df, adult_df):

    # --- Data setup ---
    years = sorted(
        list(
            set(early_childhood_df['year'].unique())
            | set(tertiary_df['year'].unique())
            | set(adult_df['year'].unique())
        )
    )

    drop_regions = [
        "European Union - 27 countries (from 2020)",
        "Euro area – 20 countries (from 2023)",
        "Euro area - 19 countries  (2015-2022)"
    ]
    early_childhood_df = early_childhood_df.loc[~early_childhood_df["country"].isin(drop_regions)]
    tertiary_df = tertiary_df.loc[~tertiary_df["country"].isin(drop_regions)]
    adult_df = adult_df.loc[~adult_df["country"].isin(drop_regions)]

    countries = sorted(
        list(
            set(early_childhood_df['country'].unique())
            | set(tertiary_df['country'].unique())
            | set(adult_df['country'].unique())
        )
    )

    # --- Layout ---
    layout = html.Div([
        html.H3("Education Level Comparison Between Countries",
            style={
                "fontWeight": "400",
                "textAlign": "center",
                "margin": "2.5rem auto 1.5rem auto",
                "fontSize": "1.5rem",
                "lineHeight": "1.6",
                "maxWidth": "800px",
            }),

        html.H4("Compare education distributions by year and country",
            style={
                "fontSize": "15px",
                "fontWeight": "400",
                "textAlign": "center",
                "margin": "0 auto 1rem auto",
                "color": "#4B5563",
                "maxWidth": "800px",
                "lineHeight": "1.6"
            }),

        html.Div([
            dcc.Dropdown(
                id="edu-year-dropdown",
                options=[{"label": str(y), "value": y} for y in sorted(years, reverse=True)],
                value=years[-1] if years else None,
                clearable=False,
                style={"width": "200px", "margin": "0 auto 20px auto"}
            ),

            html.Div([
                html.Div([
                    html.Label("Country A", style={"fontWeight": "bold"}),
                    dcc.Dropdown(
                        id="edu-country-a-dropdown",
                        options=[{"label": c, "value": c} for c in countries],
                        value="Finland",
                        clearable=False
                    )
                ], style={"width": "45%"}),

                html.Div([
                    html.Label("Country B", style={"fontWeight": "bold"}),
                    dcc.Dropdown(
                        id="edu-country-b-dropdown",
                        options=[{"label": c, "value": c} for c in countries],
                        value="Sweden",
                        clearable=False
                    )
                ], style={"width": "45%"}),
            ], style={"display": "flex", "justifyContent": "space-between", "gap": "5%"})
        ]),

        html.Div([
            dcc.Graph(id="edu-country-a-graph", style={"width": "45%"}),
            dcc.Graph(id="edu-country-b-graph", style={"width": "45%"})
        ], style={"display": "flex", "justifyContent": "space-around", "gap": "5%", "marginTop": "30px"}),

    ], className="my-8")

    # --- Callback ---
    @app.callback(
        Output("edu-country-a-graph", "figure"),
        Output("edu-country-b-graph", "figure"),
        Input("edu-year-dropdown", "value"),
        Input("edu-country-a-dropdown", "value"),
        Input("edu-country-b-dropdown", "value")
    )
    def update_graphs(selected_year, country_a, country_b):
        if not selected_year or not country_a or not country_b:
            return {}, {}

        def build_country_df(country):
            data = []
            for label, df in [
                ("Early childhood education", early_childhood_df),
                ("Tertiary education", tertiary_df),
                ("Adult education", adult_df)
            ]:
                row = df[(df["country"] == country) & (df["year"] == selected_year)]
                if not row.empty:
                    value = float(row.iloc[0]["value"])
                    data.append({"Education type": label, "Percentage": value})
            return pd.DataFrame(data)

        # Match exact labels used in your data
        color_map = {
            "Early childhood education": "#1f77b4",
            "Tertiary education": "#ff7f0e",
            "Adult education": "#2ca02c"
        }

        def make_histogram(df, country_name):
            if df.empty:
                fig = px.bar(title=f"No data for {country_name} in {selected_year}")
                fig.update_layout(
                    xaxis_title=None, yaxis_title=None,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                return fig

            # Apply consistent color mapping
            fig = px.bar(
                df,
                x="Education type",
                y="Percentage",
                title=f"{country_name} ({selected_year})",
                color="Education type",
                text_auto=".1f",
                color_discrete_map=color_map
            )

            fig.update_layout(
                showlegend=False,
                yaxis_title="Percentage",
                xaxis_title=None,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            return fig

        df_a = build_country_df(country_a)
        df_b = build_country_df(country_b)

        fig_a = make_histogram(df_a, country_a)
        fig_b = make_histogram(df_b, country_b)

        return fig_a, fig_b


    return layout
