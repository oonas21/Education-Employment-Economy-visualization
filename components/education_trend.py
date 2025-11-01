from dash import html, dcc
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output
from assets.country_colors import country_colors

def education_trend_component(app, early_childhood_df, tertiary_df, adult_df):


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


    layout = html.Div([
        html.H3("Education Trends", 
            style={
            "fontWeight": "400",          # light-medium weight (like before)
            "textAlign": "center",        # center align
            "margin": "2.5rem auto 1.5rem auto",  # more space on top (≈mt-6)
            "fontSize": "1.5rem",         # same visual size as text-lg / ~24px
            "lineHeight": "1.6",          # balanced vertical spacing
            "maxWidth": "800px",          # keeps it readable
        }),

        # Single dropdown for both graphs
        dcc.Dropdown(
            id="education-country-dropdown",
            options=[{"label": c, "value": c} for c in countries],
            value="Finland" if countries else None,
            clearable=False,
            style={"width": "300px", "margin": "0 auto", "marginBottom": "10px"}
        ),

        # Graphs side by side (or stacked for smaller screens)
        html.Div([
            dcc.Graph(id="education-trend", style={"flex": "1", "height": "600px"}),
        ], style={"display": "flex", "gap": "2%", "flexWrap": "wrap"})
    ])

    # --- Single callback for both graphs ---
    @app.callback(
        Output("education-trend", "figure"),
        Input("education-country-dropdown", "value")
    )
    def update_edu_trends(selected_countries):
        if not selected_countries:
            return {}

        if isinstance(selected_countries, str):
            selected_countries = [selected_countries]

        # Filter by country
        df_childhood = early_childhood_df[early_childhood_df['country'].isin(selected_countries)].sort_values("year")
        df_ter = tertiary_df[tertiary_df['country'].isin(selected_countries)].sort_values("year")
        df_adul = adult_df[adult_df['country'].isin(selected_countries)].sort_values("year")

        df_childhood["indicator"] = "Early childhood"
        df_ter["indicator"] = "Tertiary"
        df_adul["indicator"] = "Adult learning"
        df_all = pd.concat([df_childhood, df_ter, df_adul])

        # --- Mean lines ---
        mean_childhood = early_childhood_df.groupby("year")["value"].mean().reset_index()
        mean_childhood["indicator"] = "Mean - Early childhood"

        mean_ter = tertiary_df.groupby("year")["value"].mean().reset_index()
        mean_ter["indicator"] = "Mean - Tertiary"

        mean_adul = adult_df.groupby("year")["value"].mean().reset_index()
        mean_adul["indicator"] = "Mean - Adult learning"

        means_df = pd.concat([mean_childhood, mean_ter, mean_adul])

        # Color map for both solid and dashed lines
        color_map = {
            "Early childhood": "#1f77b4",
            "Tertiary": "#ff7f0e",
            "Adult learning": "#2ca02c"
        }

        # --- Main trend lines ---
        fig_edu = px.line(
            df_all,
            x="year",
            y="value",
            color="indicator",
            title="Education Indicators Over Time",
            labels={"value": "Percentage (%)", "year": "Year"},
            color_discrete_map=color_map
        )

        # --- Add dashed mean lines manually ---
        for ind, df_mean in means_df.groupby("indicator"):
            if "Early childhood" in ind:
                color = color_map["Early childhood"]
            elif "Tertiary" in ind:
                color = color_map["Tertiary"]
            else:
                color = color_map["Adult learning"]

            fig_edu.add_scatter(
                x=df_mean["year"],
                y=df_mean["value"],
                mode="lines",
                name=ind,
                line=dict(dash="dash", width=3, color=color),
                hoverinfo="skip"
            )

        # --- Order legend and layout ---
        desired_order = [
            "Early childhood",
            "Mean - Early childhood",
            "Tertiary",
            "Mean - Tertiary",
            "Adult learning",
            "Mean - Adult learning"
        ]
        for trace in fig_edu.data:
            if trace.name in desired_order:
                trace.legendrank = desired_order.index(trace.name)

        fig_edu.update_layout(
            legend=dict(traceorder="normal"),
            yaxis_title="Education (%)",
            legend_title_text="Indicator",
            title_x=0.5
        )

        return fig_edu

    return layout
