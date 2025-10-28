import httpx, os
from dotenv import load_dotenv

load_dotenv()
GTFS = os.getenv("GTFS_RT_URL")

async def fetch_gtfs():
    async with httpx.AsyncClient() as client:
        r = await client.get(GTFS)
        if r.status_code == 200:
            return r.json()
        return {"error": f"Failed {r.status_code}"}

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
