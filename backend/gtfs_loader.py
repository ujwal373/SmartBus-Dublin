import zipfile
import pandas as pd
import networkx as nx
import os

def load_gtfs_as_graph(gtfs_zip):
    """
    Minimal GTFS → NetworkX converter.
    Builds stop graph using stop_times.txt and trips.txt.
    """
    if not os.path.exists(gtfs_zip):
        raise FileNotFoundError(f"GTFS file not found: {gtfs_zip}")

    with zipfile.ZipFile(gtfs_zip, "r") as z:
        stops = pd.read_csv(z.open("stops.txt"))
        stop_times = pd.read_csv(z.open("stop_times.txt"))
        trips = pd.read_csv(z.open("trips.txt"))

    G = nx.DiGraph()
    for _, row in stops.iterrows():
        G.add_node(row["stop_id"], name=row["stop_name"],
                   lat=row["stop_lat"], lon=row["stop_lon"])

    for trip_id, group in stop_times.groupby("trip_id"):
        seq = group.sort_values("stop_sequence")["stop_id"].tolist()
        for i in range(len(seq) - 1):
            G.add_edge(seq[i], seq[i+1], trip_id=trip_id)

    print(f"✅ Built graph with {G.number_of_nodes()} stops and {G.number_of_edges()} edges.")
    return G
