import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output


# --- Load Eurostat CSV ---
with open("4_1_early_leavers.csv", encoding="utf-8") as f:
    lines = f.readlines()

# Find where header row starts ("TIME;2004;2005;...")
start_idx = next(i for i, line in enumerate(lines) if line.startswith("TIME;"))

# Load, using that line as header
df = pd.read_csv(
    "4_1_early_leavers.csv",
    sep=";",
    skiprows=start_idx,
    na_values=[":", "bu", "b", "u"],  # flags treated as NaN
)

# Now first column = "TIME", second = "GEO (Labels)"
df = df.rename(columns={"TIME": "country", "GEO (Labels)": "country"})

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
