import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from delay_analyzer import detect_delays

st.title("🚍 SmartBus Dublin – Live Map")

# fetch bus data as before
data = requests.get("http://127.0.0.1:8000/buses").json()
df = detect_delays(data)

# Base map
m = folium.Map(location=[53.3498, -6.2603], zoom_start=9, tiles="CartoDB positron")

# Add markers for each vehicle
if "entity" in data and len(data["entity"]) > 0:
    for ent in data["entity"]:
        pos = ent["position"]
        trip = ent["trip"]
        lat, lon = pos["latitude"], pos["longitude"]
        route_id = trip.get("route_id", "Unknown")

        folium.CircleMarker(
            location=[lat, lon],
            radius=4,
            color="blue",
            fill=True,
            fill_opacity=0.7,
            popup=f"Route: {route_id}"
        ).add_to(m)
else:
    st.warning("No live vehicles available right now.")

# Render map
st_data = st_folium(m, width=700, height=500)
st.subheader("🚦 Delay Detection Snapshot")
st.dataframe(df.head())
