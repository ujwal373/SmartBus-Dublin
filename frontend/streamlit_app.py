import streamlit as st
from streamlit_autorefresh import st_autorefresh
import requests
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import sys, os, time, pickle
import networkx as nx
import plotly.express as px

# Import delay analyzer
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend")))
from delay_analyzer import detect_delays

# --- Load static Dublin Bus graph ---
graph_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "dublin_bus_graph.gpickle"))
G = None
if os.path.exists(graph_path):
    with open(graph_path, "rb") as f:
        G = pickle.load(f)
else:
    st.warning("⚠️ Graph not found. Please run graph_builder.py first.")

# ---- Streamlit setup ----
st.set_page_config(page_title="SmartBus Dublin", page_icon="🚍", layout="wide")
st.title("🚍 SmartBus Dublin – Live Map")
st.caption("AI-assisted monitoring for a self-healing Dublin bus network")

# ---- Sidebar Panel ----
st.sidebar.title("📊 Network Overview")

# Auto-refresh every 60 seconds
# ---- Smart refresh toggle ----
refresh_toggle = st.sidebar.checkbox("🔄 Auto-refresh every 60s", value=True)

if refresh_toggle:
    # initialize timestamp
    if "last_refresh" not in st.session_state:
        st.session_state["last_refresh"] = time.time()

    # check if 60 seconds passed since last refresh
    elapsed = time.time() - st.session_state["last_refresh"]
    if elapsed > 60:
        st.session_state["last_refresh"] = time.time()
        st.experimental_rerun()
else:
    st.sidebar.caption("⏸️ Auto-refresh paused. Use manual refresh from Streamlit UI.")



# ---- Fetch live GTFS data ----
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

# ---- Sidebar Stats ----
if not df.empty:
    normal = len(df[df["status"] == "normal"])
    slow = len(df[df["status"] == "slow"])
    delayed = len(df[df["status"] == "delayed"])

    st.sidebar.metric("🚌 Active Vehicles", count)
    st.sidebar.metric("✅ Normal", normal)
    st.sidebar.metric("⚠️ Slow", slow)
    st.sidebar.metric("⛔ Delayed", delayed)

    summary = df["status"].value_counts().reset_index()
    summary.columns = ["Status", "Count"]
    fig = px.pie(summary, names="Status", values="Count",
                 color="Status",
                 color_discrete_map={"normal": "green", "slow": "orange", "delayed": "red"})
    st.sidebar.plotly_chart(fig, use_container_width=True)
else:
    st.sidebar.info("⏳ Waiting for live data...")

# ---- Status Banner ----
st.markdown(
    f"**Last update:** {time.strftime('%H:%M:%S')}  |  🚌 Active vehicles: {count}  |  ⚠️ Detected delays: {len(df)}"
)

# ---- Base Map ----
m = folium.Map(location=[53.3498, -6.2603], zoom_start=12, tiles="CartoDB positron")

# --- Layer Controls ---
bus_layer = folium.FeatureGroup(name="🚌 Live Buses").add_to(m)
gtfs_layer = folium.FeatureGroup(name="🗺️ GTFS Network").add_to(m)

# --- Draw static GTFS network (gray lines) ---
if G:
    for u, v in list(G.edges())[:2000]:  # Limit for performance
        try:
            u_lat, u_lon = G.nodes[u]["lat"], G.nodes[u]["lon"]
            v_lat, v_lon = G.nodes[v]["lat"], G.nodes[v]["lon"]
            folium.PolyLine(
                locations=[[u_lat, u_lon], [v_lat, v_lon]],
                color="gray",
                weight=1,
                opacity=0.3
            ).add_to(gtfs_layer)
        except KeyError:
            continue

# --- Add clustered live bus markers ---
cluster = MarkerCluster().add_to(bus_layer)

if "entity" in data and count > 0 and not df.empty:
    for _, row in df.iterrows():
        lat, lon = row["latitude"], row["longitude"]
        vehicle_id = row["vehicle_id"]
        status = row["status"]
        movement = round(row["movement"], 6)
        color_map = {"normal": "green", "slow": "orange", "delayed": "red"}
        color = color_map.get(status, "blue")

        popup_html = f"""
        <b>Vehicle:</b> {vehicle_id}<br>
        <b>Status:</b> {status.title()}<br>
        <b>Movement:</b> {movement}<br>
        <b>Last update:</b> {time.strftime('%H:%M:%S')}
        """
        folium.CircleMarker(
            location=[lat, lon],
            radius=5,
            color=color,
            fill=True,
            fill_opacity=0.85,
            popup=popup_html
        ).add_to(cluster)
else:
    st.warning("No live vehicles available right now or data still initializing...")

# Add layer control to toggle visibility
folium.LayerControl(collapsed=False).add_to(m)

# ---- Render Map ----
st_data = st_folium(m, width=900, height=550)

# ---- Delay Table ----
st.subheader("🚦 Delay Detection Snapshot")

def highlight_status(row):
    color = ""
    if row["status"] == "delayed":
        color = "background-color: #ffcccc"
    elif row["status"] == "slow":
        color = "background-color: #fff3cd"
    elif row["status"] == "normal":
        color = "background-color: #d4edda"
    else:
        color = ""
    return [color] * len(row)

if not df.empty:
    st.dataframe(df.style.apply(highlight_status, axis=1))
else:
    st.info("No delays detected yet — monitoring in progress...")
