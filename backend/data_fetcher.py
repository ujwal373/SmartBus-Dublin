import os
import httpx
from dotenv import load_dotenv

load_dotenv()

async def fetch_gtfs():
    """
    Fetch and decode GTFS-Realtime feed from NTA (Protocol Buffers format).
    """
    url = os.getenv("GTFS_RT_URL")
    api_key = os.getenv("API_KEY")
    headers = {"x-api-key": api_key}

    feed = gtfs_realtime_pb2.FeedMessage()

    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(url, headers=headers)
        if r.status_code == 200:
            feed.ParseFromString(r.content)

            # Convert to Python dict for JSON response
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
            return {"entity": entities, "count": len(entities)}
        else:
            return {"error": f"GTFS fetch failed ({r.status_code})"}
