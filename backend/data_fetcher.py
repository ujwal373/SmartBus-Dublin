import os
import httpx
from dotenv import load_dotenv

load_dotenv()

async def fetch_gtfs():
    """
    Fetch live Dublin Bus GTFS-Realtime data using NTA API key.
    """
    url = os.getenv("GTFS_RT_URL")
    api_key = os.getenv("API_KEY")
    headers = {"x-api-key": api_key}

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            r = await client.get(url, headers=headers)
            if r.status_code == 200:
                return r.json()
            else:
                return {
                    "error": f"GTFS fetch failed ({r.status_code})",
                    "details": r.text[:200]
                }
        except Exception as e:
            return {"error": str(e)}


async def fetch_weather():
    url = "https://prodapi.metweb.ie/observations/dublin"
    async with httpx.AsyncClient() as c:
        r = await c.get(url)
        if r.status_code == 200:
            data = r.json()
            latest = data["observations"][-1] if "observations" in data else {}
            return {
                "temp": latest.get("airTemperature", None),
                "windSpeed": latest.get("windSpeed", None),
                "rainfall": latest.get("rainfall", None),
                "timestamp": latest.get("time", None),
            }
        return {"error": f"Weather fetch failed ({r.status_code})"}
