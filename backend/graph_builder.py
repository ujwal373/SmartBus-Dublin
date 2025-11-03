import os
import networkx as nx
from networkx.readwrite import gpickle
from gtfs_loader import load_gtfs_as_graph


def build_dublin_bus_graph():
    """
    Build a graph of the Dublin Bus GTFS static feed.
    Reads GTFS zip, converts to stop-level graph, and saves as .gpickle
    """
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    gtfs_path = os.path.join(data_dir, "gtfs_dublin.zip")

    if not os.path.exists(gtfs_path):
        raise FileNotFoundError(f"GTFS file not found at {gtfs_path}")

    print("📦 Loading GTFS feed and building graph, please wait...")

    G = load_gtfs_as_graph(gtfs_path)
    print(f"✅ Built graph with {G.number_of_nodes()} stops and {G.number_of_edges()} edges.")

    gpickle.write_gpickle(G, os.path.join(data_dir, "dublin_bus_graph.gpickle"))
    print("✅ Graph saved to data/dublin_bus_graph.gpickle")

    return G


if __name__ == "__main__":
    build_dublin_bus_graph()
