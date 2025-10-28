from fastapi import FastAPI
from data_fetcher import fetch_gtfs, fetch_weather

app = FastAPI(title="SmartBus Dublin")

@app.get("/")
def root():
    return {"status": "running"}

@app.get("/buses")
async def get_buses():
    data = await fetch_gtfs()
    return data

@app.get("/weather")
async def get_weather():
    weather = await fetch_weather()
    return weather
