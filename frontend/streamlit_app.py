import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from delay_analyzer import detect_delays



st.title("🚍 SmartBus Dublin – Live Map")

resp = requests.get("http://127.0.0.1:8000/buses")
data = resp.json()

m = folium.Map(location=[53.35, -6.26], zoom_start=12)

if "entity" in data:
    for ent in data["entity"]:
        if "vehicle" in ent:
            v = ent["vehicle"]
            pos = v["position"]
            folium.CircleMarker(
                location=[pos["latitude"], pos["longitude"]],
                radius=4, color="blue",
                popup=v["trip"].get("route_id", "Unknown")
            ).add_to(m)

st_folium(m, width=700, height=500)

# fetch bus data as before
data = requests.get("http://127.0.0.1:8000/buses").json()
df = detect_delays(data)

st.subheader("🚦 Delay Detection Snapshot")
st.dataframe(df.head())
