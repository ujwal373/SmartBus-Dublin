import pandas as pd
import time

def detect_delays(data, cache={}):
    """
    Detect buses that are likely delayed based on reduced speed or
    repeated positions.
    """
    if "entity" not in data:
        return pd.DataFrame()

    records = []
    now = time.time()

    for ent in data["entity"]:
        v = ent.get("vehicle", {})
        pos = v.get("position", {})
        trip = v.get("trip", {})
        if pos and trip:
            records.append({
                "route": trip.get("route_id"),
                "lat": pos.get("latitude"),
                "lon": pos.get("longitude"),
                "timestamp": now,
                "vehicle_id": v.get("vehicle", {}).get("id", ent.get("id"))
            })

    df = pd.DataFrame(records)

    # Basic heuristic: repeated identical coordinates over 2+ snapshots → possible delay
    if "prev" in cache:
        merged = df.merge(cache["prev"], on="id", suffixes=("", "_prev"))
        df["stopped"] = ((merged["lat"] - merged["lat_prev"]).abs() < 0.0001) & \
                        ((merged["lon"] - merged["lon_prev"]).abs() < 0.0001)
    cache["prev"] = df.copy()
    return df
