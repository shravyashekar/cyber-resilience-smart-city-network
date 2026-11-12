"""NetworkX model of a fictional smart city. All operations are in-memory only."""
import networkx as nx

SERVICES = {
    "Hospital": {"tier": 1, "criticality": "Critical", "color": "#ef476f"},
    "Emergency Dispatch": {"tier": 1, "criticality": "Critical", "color": "#ef476f"},
    "Traffic Control": {"tier": 2, "criticality": "High", "color": "#ffd166"},
    "Water Supply": {"tier": 2, "criticality": "High", "color": "#ffd166"},
    "Power Grid": {"tier": 1, "criticality": "Critical", "color": "#ef476f"},
    "Public Display": {"tier": 3, "criticality": "Low", "color": "#06d6a0"},
}
EDGES = [("Hospital", "Emergency Dispatch"), ("Hospital", "Power Grid"),
         ("Emergency Dispatch", "Traffic Control"), ("Traffic Control", "Power Grid"),
         ("Water Supply", "Power Grid"), ("Public Display", "Traffic Control"),
         ("Hospital", "Water Supply"), ("Emergency Dispatch", "Public Display")]


def create_smart_city_network():
    graph = nx.Graph()
    for name, attrs in SERVICES.items():
        graph.add_node(name, **attrs, status="Active", role="primary")
        graph.add_node(name + " Backup", **attrs, status="Standby", role="backup", service=name)
        graph.add_edge(name, name + " Backup", kind="failover")
    for a, b in EDGES:
        graph.add_edge(a, b, kind="service")
    return graph
