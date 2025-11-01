import os
import time
import httpx
from dotenv import load_dotenv
from google.transit import gtfs_realtime_pb2

load_dotenv()

# Simple in-memory cache to reduce API calls (avoid 429 errors)
_last_fetch = {"time": 0, "data": None}

async def fetch_gtfs():
    """
    Fetch and decode GTFS-Realtime feed (Protocol Buffers format)
    from the National Transport Authority (TFI Dublin Bus).
    Cached for 60 seconds to respect API rate limits.
    """
    url = os.getenv("GTFS_RT_URL")
    api_key = os.getenv("API_KEY")
    headers = {"x-api-key": api_key}

    # --- Caching logic ---
    now = time.time()
    if _last_fetch["data"] and (now - _last_fetch["time"] < 60):
        return _last_fetch["data"]

    feed = gtfs_realtime_pb2.FeedMessage()

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(url, headers=headers)

            # Handle HTTP errors explicitly
            if r.status_code == 200:
                feed.ParseFromString(r.content)

                entities = []
                for entity in feed.entity:
                    if entity.HasField("vehicle"):
                        v = entity.vehicle
                        entities.append({
                            "id": entity.id,
                            "trip": {
                                "route_id": v.trip.route_id,
                                "start_time": v.trip.start_time,
                                "trip_id": v.trip.trip_id
                            },
                            "position": {
                                "latitude": v.position.latitude,
                                "longitude": v.position.longitude
                            },
                            "timestamp": v.timestamp
                        })

                result = {"entity": entities, "count": len(entities)}
                _last_fetch.update({"time": now, "data": result})
                return result

            elif r.status_code == 429:
                return {"error": "Rate limit reached. Please wait a minute before refreshing."}
            else:
                return {"error": f"GTFS fetch failed ({r.status_code})"}

    except Exception as e:
        return {"error": f"Exception during GTFS fetch: {str(e)}"}


async def fetch_weather():
    """
    Fetch current weather data for Dublin from Met Éireann (public endpoint).
    """
    url = "https://prodapi.metweb.ie/observations/dublin"
    try:
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
    except Exception as e:
        return {"error": f"Exception during weather fetch: {str(e)}"}
