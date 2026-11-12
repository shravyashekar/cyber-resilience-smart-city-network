"""Run a complete synthetic scenario and simulated resilience response."""
from data_generator import generate_traffic
from anomaly_detector import train_detector, score_traffic
from network_topology import SERVICES, create_smart_city_network
from risk_assessment import SCENARIO_SEVERITY, assess_risk
from self_healing import respond
from incident_triage import triage_alerts


def run_simulation(scenario="DoS", service="Hospital", rows=240, seed=17):
    if scenario not in ("Normal", "DoS", "Port Scan", "Malware-like"):
        raise ValueError("Unknown simulation scenario")
    if service not in SERVICES:
        raise ValueError("Choose a primary city service")
    # The selected scenario only shapes the generated traffic. Everything
    # after scoring is decided from the detector's alerts.
    data = generate_traffic(rows=rows, seed=seed, scenario=scenario, target_service=service)
    model = train_detector(seed)
    scored = score_traffic(model, data)
    triage = triage_alerts(scored, service)
    graph = create_smart_city_network()
    detected_threat = triage["inferred_threat"] if triage["incident_detected"] else "Normal"
    severity = SCENARIO_SEVERITY[detected_threat]
    service_details = SERVICES[service]
    risk_assessment = assess_risk(
        severity, service_details["tier"], service_details["civic_impact"]
    )
    if not triage["incident_detected"]:
        recovered = graph.copy()
        actions = {"service": service, "isolated": False, "backup": service + " Backup",
                   "tier": graph.nodes[service]["tier"], "response_mode": "No action",
                   "response_detail": "No incident detected for this service; paths left unchanged.",
                   "risk_assessment": risk_assessment, "risk_score": risk_assessment["risk_score"],
                   "rerouted": False, "critical_services_reachable": True,
                   "verification": {}, "response_taken": False, "incident_present": False}
    else:
        recovered, actions = respond(graph, service, severity, risk_assessment)
        actions["response_taken"] = actions["response_mode"] != "Monitor"
        actions["incident_present"] = True
    actions["triage"] = triage
    actions["detected_threat"] = detected_threat
    actions["simulated_scenario"] = scenario
    return scored, graph, recovered, actions
