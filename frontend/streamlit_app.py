import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import sys, os, time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend")))
from delay_analyzer import detect_delays

st.set_page_config(page_title="SmartBus Dublin", page_icon="🚍", layout="wide")

st.title("🚍 SmartBus Dublin – Live Map")
st.caption("AI-assisted monitoring for a self-healing Dublin bus network")

# ---- Fetch bus data safely ----
try:
    resp = requests.get("http://127.0.0.1:8000/buses", timeout=10)
    data = resp.json()
    if "error" in data:
        st.error(f"Backend error: {data['error']}")
        st.stop()
except Exception as e:
    st.error(f"❌ Cannot connect to backend: {e}")
    st.stop()

# ---- Detect delays ----
df = detect_delays(data)
count = len(data.get("entity", []))

# ---- Status Banner ----
st.markdown(
    f"**Last update:** {time.strftime('%H:%M:%S')}  |  🚌 Active vehicles: {count}  |  ⚠️ Detected delays: {len(df)}"
)

# ---- Base map ----
m = folium.Map(location=[53.3498, -6.2603], zoom_start=9, tiles="CartoDB positron")

if "entity" in data and count > 0:
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

# ---- Render map ----
st_data = st_folium(m, width=750, height=500)

# ---- Delay Table ----
st.subheader("🚦 Delay Detection Snapshot")
if not df.empty:
    st.dataframe(df)
else:
    st.info("No delays detected yet — monitoring in progress...")
