import os
from gtfs_loader import load_gtfs_as_graph
import networkx as nx

def build_dublin_bus_graph():
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    gtfs_path = os.path.join(data_dir, "gtfs_dublin.zip")

    G = load_gtfs_as_graph(gtfs_path)
    nx.write_gpickle(G, os.path.join(data_dir, "dublin_bus_graph.gpickle"))
    print("✅ Graph built successfully and saved!")
    return G

if __name__ == "__main__":
    build_dublin_bus_graph()


def build_dublin_bus_graph(gtfs_path="../data/gtfs_dublin.zip"):
    """
    Build a graph of the Dublin Bus GTFS static feed using city2graph.gtfs.
    """
    if not os.path.exists(gtfs_path):
        raise FileNotFoundError(f"GTFS file not found: {gtfs_path}")

    print("📦 Loading GTFS feed, please wait...")

    # Load GTFS feed and build the stop graph
    feed = gtfs.GTFS(gtfs_path)
    G = feed.to_graph(stop_level=True)   # stop_level=True builds stop-based graph

    print(f"✅ Graph built successfully — {G.number_of_nodes()} stops, {G.number_of_edges()} edges")

    nx.write_gpickle(G, "../data/dublin_bus_graph.gpickle")
    return G

if __name__ == "__main__":
    build_dublin_bus_graph()