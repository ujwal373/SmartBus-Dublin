import pandas as pd
import time

cache = {"prev": None, "last_time": 0}

def detect_delays(data):
    entities = data.get("entity", [])
    if not entities:
        return pd.DataFrame()

    # --- Flatten current data ---
    df = pd.json_normalize(entities)
    df = df.loc[:, ~df.columns.duplicated()]

    # Normalize column names
    if "vehicle.vehicle.id" in df.columns:
        df.rename(columns={"vehicle.vehicle.id": "vehicle_id"}, inplace=True)
    elif "vehicle_id" not in df.columns and "id" in df.columns:
        df.rename(columns={"id": "vehicle_id"}, inplace=True)

    # Convert numeric types
    df["latitude"] = df["position.latitude"].astype(float)
    df["longitude"] = df["position.longitude"].astype(float)
    df["timestamp"] = df["timestamp"].astype(float)

    # --- Delay detection logic ---
    if cache["prev"] is not None:
        merged = df.merge(
            cache["prev"], on="vehicle_id", suffixes=("", "_prev"), how="inner"
        )

        merged["movement"] = (
            (merged["latitude"] - merged["latitude_prev"]) ** 2 +
            (merged["longitude"] - merged["longitude_prev"]) ** 2
        ) ** 0.5

        # Classify movement severity
        def classify_move(x):
            if x < 0.00003:
                return "delayed"      # almost stationary
            elif x < 0.0001:
                return "slow"         # moving slowly
            else:
                return "normal"       # good flow

        merged["status"] = merged["movement"].apply(classify_move)

        cache["prev"] = df

        # Return concise DataFrame for display
        return merged[["vehicle_id", "latitude", "longitude", "movement", "status", "timestamp"]]
    else:
        cache["prev"] = df
        return pd.DataFrame()
