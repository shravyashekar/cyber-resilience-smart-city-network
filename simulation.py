"""Run a complete synthetic scenario and simulated resilience response."""
from data_generator import generate_traffic
from anomaly_detector import train_detector, score_traffic
from network_topology import create_smart_city_network
from self_healing import respond


def run_simulation(scenario="DoS", service="Hospital", rows=240, seed=17):
    if scenario not in ("Normal", "DoS", "Port Scan", "Malware-like"):
        raise ValueError("Unknown simulation scenario")
    # Generate records directly from the selected event distribution so the
    # displayed label always matches the features being scored.
    data = generate_traffic(rows=rows, seed=seed, scenario=scenario)
    model = train_detector(seed)
    scored = score_traffic(model, data)
    graph = create_smart_city_network()
    severity = "Critical" if scenario == "DoS" else "High"
    if scenario == "Normal":
        recovered = graph.copy()
        actions = {"service": service, "isolated": False, "backup": service + " Backup",
                   "tier": graph.nodes[service]["tier"], "response_mode": "No action",
                   "impact_score": 0, "rerouted": False, "critical_services_reachable": True,
                   "verification": {}, "response_taken": False}
    else:
        recovered, actions = respond(graph, service, severity)
        actions["response_taken"] = True
    return scored, graph, recovered, actions
