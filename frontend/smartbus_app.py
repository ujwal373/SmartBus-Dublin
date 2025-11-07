import os, time, requests, pickle
import streamlit as st
import folium
from streamlit_folium import st_folium
import networkx as nx

# --- Streamlit setup ---
st.set_page_config(page_title="SmartBus Dublin", page_icon="🚌", layout="wide")
st.title("🚌 SmartBus Dublin — Live Map")
st.caption("City2Graph + GTFS-Realtime visualized for DublinBus")

# --- Configurable constants ---
API_URL = "https://api.nationaltransport.ie/gtfsr/v1/DublinBus?format=json"
API_KEY = os.getenv("API_KEY", "")
GRAPH_PATH = os.path.join("data", "dublin_bus_graph.gpickle")

# --- Smart caching of live data ---
@st.cache_data(ttl=60)
def fetch_buses():
    headers = {"x-api-key": API_KEY}
    try:
        r = requests.get(API_URL, headers=headers, timeout=10)
        if r.status_code != 200:
            return {"error": f"GTFS fetch failed ({r.status_code})"}
        data = r.json()
        entities = []
        for ent in data.get("entity", []):
            v = ent.get("vehicle", {})
            pos = v.get("position", {})
            trip = v.get("trip", {})
            entities.append({
                "id": ent.get("id"),
                "route": trip.get("route_id"),
                "lat": pos.get("latitude"),
                "lon": pos.get("longitude"),
                "ts": v.get("timestamp"),
            })
        return {"entity": entities, "count": len(entities)}
    except Exception as e:
        return {"error": str(e)}

# --- Load static City2Graph network if available ---
G = None
if os.path.exists(GRAPH_PATH):
    with open(GRAPH_PATH, "rb") as f:
        G = pickle.load(f)
    st.sidebar.success(f"Loaded city graph: {G.number_of_nodes()} stops, {G.number_of_edges()} edges")
else:
    st.sidebar.warning("Static graph not found (run graph_builder.py to create it)")

# --- Sidebar controls ---
auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh every 60 s", True)
if auto_refresh:
    st_autorefresh = st.sidebar.button("Manual refresh now")

# --- Fetch live bus data ---
data = fetch_buses()
if "error" in data:
    st.error(data["error"])
    st.stop()

count = data["count"]
st.markdown(f"**Last update:** {time.strftime('%H:%M:%S')} | 🚌 Active buses: {count}")

# --- Create base map (Dublin center) ---
m = folium.Map(location=[53.3498, -6.2603], zoom_start=12, tiles="CartoDB positron")

# --- Draw small sample of static graph for context ---
if G:
    for u, v in list(G.edges())[:1000]:
        try:
            u_lat, u_lon = G.nodes[u]["lat"], G.nodes[u]["lon"]
            v_lat, v_lon = G.nodes[v]["lat"], G.nodes[v]["lon"]
            folium.PolyLine([[u_lat, u_lon], [v_lat, v_lon]],
                            color="gray", weight=1, opacity=0.3).add_to(m)
        except KeyError:
            continue

# --- Plot live buses ---
for ent in data["entity"]:
    lat, lon = ent["lat"], ent["lon"]
    if not lat or not lon:
        continue
    route = ent.get("route", "Unknown")
    folium.CircleMarker(
        location=[lat, lon],
        radius=4,
        color="blue",
        fill=True,
        fill_opacity=0.8,
        popup=f"Route {route}"
    ).add_to(m)

# --- Render map ---
st_folium(m, width=900, height=600)

# --- Footer ---
st.caption("Data © TFI Realtime | Visualization by SmartBus Dublin (2025)")
