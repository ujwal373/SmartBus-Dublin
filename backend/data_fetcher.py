import httpx

async def fetch_weather():
    """Fetch current weather observations for Dublin from Met Éireann"""
    url = "https://prodapi.metweb.ie/observations/dublin"
    async with httpx.AsyncClient() as c:
        r = await c.get(url)
        if r.status_code == 200:
            data = r.json()
            # optional: extract key parts
            latest = data["observations"][-1] if "observations" in data else {}
            return {
                "temp": latest.get("airTemperature", None),
                "windSpeed": latest.get("windSpeed", None),
                "rainfall": latest.get("rainfall", None),
                "timestamp": latest.get("time", None),
            }
        return {"error": f"Weather fetch failed ({r.status_code})"}
