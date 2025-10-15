# data_loader.py
import pandas as pd
import os

def load_all_data(data_dir="data"):
    """Loads and cleans all Eurostat CSV files in the given folder."""
    dataframes = {}

    for file in os.listdir(data_dir):
        if not file.endswith(".csv"):
            continue

        path = os.path.join(data_dir, file)
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()

        # Find header row
        geo_idx = next((i for i, line in enumerate(lines) if "GEO (Labels)" in line), None)
        time_idx = next((i for i, line in enumerate(lines) if line.strip().startswith("TIME;")), None)

        if geo_idx is not None and time_idx is not None:
            skiprows = min(geo_idx, time_idx)
        elif geo_idx is not None:
            skiprows = geo_idx
        elif time_idx is not None:
            skiprows = time_idx
        else:
            print(f"⚠️ No GEO/TIME header found in {file}, skipping.")
            continue

        df = pd.read_csv(
            path,
            sep=";",
            skiprows=skiprows,
            na_values=[":", "bu", "b", "u"],
            engine="python"
        )

        geo_col = next((c for c in df.columns if "GEO" in str(c)), df.columns[0])
        df = df.rename(columns={geo_col: "country"})

        year_cols = [c for c in df.columns if str(c).strip().isdigit()]
        if not year_cols:
            if "TIME" in df.columns:
                df = df.rename(columns={"TIME": "year"})
            else:
                print(f"⚠️ No year columns found in {file}, skipping.")
                continue

        df = df.melt(id_vars=["country"], var_name="year", value_name="value")

        df = df[df["year"].astype(str).str.isnumeric()]
        df["year"] = df["year"].astype(int)

        df["value"] = (
            df["value"]
            .astype(str)
            .str.replace("\u202f", "", regex=False)
            .str.replace(" ", "", regex=False)
            .str.replace(",", ".", regex=False)
            .apply(lambda x: pd.to_numeric(x, errors="coerce"))
        )

        df = df.dropna(subset=["value"])
        df["source_file"] = file
        dataframes[file] = df

        print(f"✅ Processed {file} → {df.shape[0]} rows, {df['country'].nunique()} countries")

    return dataframes
