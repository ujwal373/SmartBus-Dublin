import os
import httpx
import time
from dotenv import load_dotenv
load_dotenv()

_cache = {"data": None, "time": 0}

async def fetch_gtfs():
    url = os.getenv("GTFS_RT_URL")
    api_key = os.getenv("API_KEY")
    headers = {"x-api-key": api_key}

    # if cached data < 60 sec old → reuse it
    now = time.time()
    if _cache["data"] and now - _cache["time"] < 60:
        return _cache["data"]

    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(url, headers=headers)
        if r.status_code == 200:
            raw = r.json()
            entities = []
            for e in raw.get("entity", []):
                v = e.get("vehicle", {})
                trip = v.get("trip", {})
                pos = v.get("position", {})
                entities.append({
                    "id": e.get("id"),
                    "trip": {
                        "route_id": trip.get("route_id"),
                        "trip_id": trip.get("trip_id"),
                        "direction_id": trip.get("direction_id"),
                        "start_time": trip.get("start_time")
                    },
                    "position": {
                        "latitude": pos.get("latitude"),
                        "longitude": pos.get("longitude")
                    },
                    "vehicle_id": v.get("vehicle", {}).get("id"),
                    "timestamp": v.get("timestamp")
                })
            data = {"entity": entities, "count": len(entities)}
            _cache.update({"data": data, "time": now})
            return data
        else:
            return {"error": f"GTFS fetch failed ({r.status_code})"}


async def fetch_weather():
    """
    Fetch Dublin weather from Met Éireann API
    """
    url = "https://prodapi.metweb.ie/observations/dublin"
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(url)
        if r.status_code == 200:
            data = r.json()
            latest = data["observations"][-1] if "observations" in data else {}
            return {
                "temp": latest.get("airTemperature"),
                "windSpeed": latest.get("windSpeed"),
                "rainfall": latest.get("rainfall"),
                "timestamp": latest.get("time")
            }
        else:
            return {"error": f"Weather fetch failed ({r.status_code})"}
