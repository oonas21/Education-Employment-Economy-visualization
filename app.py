import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import os

dataframes = {}

# --- Load Eurostat CSV files ---
for file in os.listdir("."):
    if file.endswith(".csv"):
        # Find header row
        with open(file, encoding="utf-8") as f:
            lines = f.readlines()
        start_idx = next(i for i, line in enumerate(lines) if line.startswith("TIME;"))

        # Load CSV
        df = pd.read_csv(
            file,
            sep=";",
            skiprows=start_idx,
            na_values=[":", "bu", "b", "u"],
        )

        # --- Transformations ---
        # Rename columns (make sure "TIME" or "GEO (Labels)" exist)
        rename_map = {}
        if "TIME" in df.columns:
            rename_map["TIME"] = "country"
        if "GEO (Labels)" in df.columns:
            rename_map["GEO (Labels)"] = "country"
        df = df.rename(columns=rename_map)

        # Melt years into rows
        df = df.melt(id_vars=["country"], var_name="year", value_name="value")

        # Keep only numeric years
        df = df[df["year"].str.isnumeric()]
        df["year"] = df["year"].astype(int)

        # Fix decimal separator and convert to float
        df["value"] = (
            df["value"]
            .astype(str)
            .str.replace(",", ".", regex=False)
            .apply(lambda x: pd.to_numeric(x, errors="coerce"))
        )

        # Drop missing
        df = df.dropna(subset=["value"])

        # Save to dictionary
        dataframes[file] = df
        print(f"Processed {file} → {df.shape[0]} rows")



# --- Create Dash app ---
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Early leavers from education and training, by citizenship"),
    html.Label("Select Year:"),
    dcc.Dropdown(
        id="year-dropdown",
        options=[{"label": str(y), "value": y} for y in sorted(df["year"].unique())],
        value=df["year"].min(),
        clearable=False
    ),
    dcc.Graph(
        id="map",
        style={"height": "800px", "width": "100%"}  
    )
])

@app.callback(
    Output("map", "figure"),
    Input("year-dropdown", "value")
)
def update_map(selected_year):
    filtered = df[df["year"] == selected_year]

    fig = px.choropleth(
        filtered,
        locations="country",
        locationmode="country names",
        color="value",
        scope="europe",
        color_continuous_scale="Viridis",
        title=f"Early leavers from education/training ({selected_year})"
    )
    fig.update_geos(fitbounds="locations")
    return fig

if __name__ == "__main__":
    app.run(debug=True)
