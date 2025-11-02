import city2graph as c2g
import networkx as nx
import os

def build_dublin_bus_graph(gtfs_path="../data/gtfs_dublin.zip"):
    """
    Build a city-scale graph from the Dublin Bus GTFS static feed.
    Converts stops, routes, and trips into a graph usable for analysis.
    """
    if not os.path.exists(gtfs_path):
        raise FileNotFoundError(f"GTFS file not found: {gtfs_path}")

    # Load GTFS feed as graph (city2graph auto-detects stops/routes/trips)
    g = c2g.load_gtfs_as_graph(gtfs_path)

    print(f"✅ Graph built successfully — {g.number_of_nodes()} stops, {g.number_of_edges()} edges")
    
    nx.write_gpickle(g, "../data/dublin_bus_graph.gpickle")
    return g

if __name__ == "__main__":
    build_dublin_bus_graph()
