"""Run a complete synthetic scenario and simulated resilience response."""
from data_generator import generate_traffic
from anomaly_detector import train_detector, score_traffic
from network_topology import SERVICES, create_smart_city_network
from risk_assessment import SCENARIO_SEVERITY, assess_risk
from self_healing import respond


def run_simulation(scenario="DoS", service="Hospital", rows=240, seed=17):
    if scenario not in ("Normal", "DoS", "Port Scan", "Malware-like"):
        raise ValueError("Unknown simulation scenario")
    if service not in SERVICES:
        raise ValueError("Choose a primary city service")
    data = generate_traffic(rows=rows, seed=seed, scenario=scenario)
    model = train_detector(seed)
    scored = score_traffic(model, data)
    graph = create_smart_city_network()
    severity = SCENARIO_SEVERITY[scenario]
    service_details = SERVICES[service]
    risk_assessment = assess_risk(
        severity, service_details["tier"], service_details["civic_impact"]
    )
    if scenario == "Normal":
        recovered = graph.copy()
        actions = {"service": service, "isolated": False, "backup": service + " Backup",
                   "tier": graph.nodes[service]["tier"], "response_mode": "No action",
                   "risk_assessment": risk_assessment, "risk_score": risk_assessment["risk_score"],
                   "rerouted": False, "critical_services_reachable": True,
                   "verification": {}, "response_taken": False, "incident_present": False}
    else:
        recovered, actions = respond(graph, service, severity, risk_assessment)
        actions["response_taken"] = actions["response_mode"] != "Monitor"
        actions["incident_present"] = True
    return scored, graph, recovered, actions
