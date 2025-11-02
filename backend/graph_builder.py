import city2graph as c2g
import networkx as nx

def build_dublin_bus_graph(gtfs_path="data/gtfs_dublin.zip"):
    g = c2g.load_gtfs_as_graph(gtfs_path, agency="Dublin Bus")

    # Optional: basic metrics
    print("Nodes:", g.number_of_nodes())
    print("Edges:", g.number_of_edges())

    nx.write_gpickle(g, "data/dublin_bus_graph.gpickle")
    return g
