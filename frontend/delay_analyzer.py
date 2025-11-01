import pandas as pd
import time

cache = {"prev": None, "last_time": 0}

def detect_delays(data):
    entities = data.get("entity", [])
    if not entities:
        return pd.DataFrame()

    # --- flatten current data ---
    df = pd.json_normalize(entities)

    # Ensure unique and clean column names
    df = df.loc[:, ~df.columns.duplicated()]
    if "vehicle.vehicle.id" in df.columns:
        df.rename(columns={"vehicle.vehicle.id": "vehicle_id"}, inplace=True)
    elif "vehicle_id" not in df.columns and "id" in df.columns:
        df.rename(columns={"id": "vehicle_id"}, inplace=True)

    # Convert numeric types
    df["latitude"] = df["position.latitude"].astype(float)
    df["longitude"] = df["position.longitude"].astype(float)
    df["timestamp"] = df["timestamp"].astype(float)

    # --- delay detection logic ---
    if cache["prev"] is not None:
        merged = df.merge(
            cache["prev"], on="vehicle_id", suffixes=("", "_prev"), how="inner"
        )

        merged["movement"] = (
            (merged["latitude"] - merged["latitude_prev"]) ** 2
            + (merged["longitude"] - merged["longitude_prev"]) ** 2
        ) ** 0.5

        delayed = merged[merged["movement"] < 0.00005]
        cache["prev"] = df
        return delayed[["vehicle_id", "latitude", "longitude", "movement", "timestamp"]]
    else:
        cache["prev"] = df
        return pd.DataFrame()
