import pandas as pd
import time

# Simple cache to remember last frame
cache = {"prev": None, "time": 0}

def detect_delays(data):
    """
    Detect potential bus delays by comparing current vs previous positions.
    Returns a DataFrame of slow or stopped vehicles.
    """
    # Convert incoming JSON to DataFrame
    if not data or "entity" not in data:
        return pd.DataFrame()

    df = pd.json_normalize(data["entity"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s", errors="coerce")

    # Rename id column for clarity
    if "id" in df.columns:
        df.rename(columns={"id": "vehicle_id"}, inplace=True)

    # If first run, just cache and return empty
    if cache["prev"] is None:
        cache["prev"] = df.copy()
        cache["time"] = time.time()
        return pd.DataFrame()

    # Ensure both have the same merge key
    if "vehicle_id" not in cache["prev"].columns:
        cache["prev"].rename(columns={"id": "vehicle_id"}, inplace=True)

    try:
        merged = df.merge(cache["prev"], on="vehicle_id", suffixes=("", "_prev"))
    except KeyError:
        # If columns still mismatch, reset cache and skip this round
        cache["prev"] = df.copy()
        return pd.DataFrame()

    # Compute distance moved (very rough proxy for delay)
    merged["moved"] = (
        (merged["position.latitude"] - merged["position.latitude_prev"]).abs() +
        (merged["position.longitude"] - merged["position.longitude_prev"]).abs()
    )

    delayed = merged[merged["moved"] < 0.0001]  # adjust threshold
    delayed = delayed[["vehicle_id", "trip.route_id", "moved", "timestamp"]]

    # Update cache
    cache["prev"] = df.copy()
    cache["time"] = time.time()

    return delayed
