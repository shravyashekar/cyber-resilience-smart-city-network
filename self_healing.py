"""Tier- and risk-aware simulated response actions for a fictional city network."""
import networkx as nx

from risk_assessment import assess_risk


def respond(graph, target, severity="High", risk_assessment=None):
    """Apply a risk threshold and service-tier policy, then verify connectivity."""
    if target not in graph or graph.nodes[target].get("role") == "backup":
        raise ValueError("Choose a primary city service")

    result = graph.copy()
    backup = target + " Backup"
    tier = result.nodes[target]["tier"]
    risk_assessment = risk_assessment or assess_risk(
        severity, tier, result.nodes[target]["civic_impact"]
    )
    risk_score = risk_assessment["risk_score"]
    incident_edges = list(result.edges(target, data=True))

    if tier == 1:
        response_mode = "Failover" if risk_score >= 70 else "Safe fallback"
    elif tier == 2:
        response_mode = "Safe fallback" if risk_score >= 55 else "Monitor"
    else:
        response_mode = "Isolation" if risk_score >= 55 else "Monitor"

    if response_mode == "Failover":
        neighbors = [(b if a == target else a, attrs) for a, b, attrs in incident_edges
                     if attrs.get("kind") == "service"]
        result.remove_edges_from([(a, b) for a, b, _ in incident_edges])
        result.nodes[target].update(status="Isolated (simulated)", isolated=True)
        result.nodes[backup].update(status="Active (failover)", role="active-backup")
        for neighbor, _attrs in neighbors:
            result.add_edge(backup, neighbor, kind="simulated-reroute")
        response_detail = "Tier 1 service isolated; backup activated and city links rerouted."
    elif response_mode == "Safe fallback":
        result.nodes[target].update(status="Safe fallback (simulated)", isolated=False)
        result.nodes[backup].update(status="Standby (ready)", role="backup")
        response_detail = "Service continues in restricted safe fallback mode."
    elif response_mode == "Isolation":
        result.remove_edges_from([(a, b) for a, b, _ in incident_edges])
        result.nodes[target].update(status="Isolated (simulated)", isolated=True)
        result.nodes[backup].update(status="Standby (ready)", role="backup")
        response_detail = "Tier 3 service isolated; its backup remains on standby."
    else:
        response_detail = "Risk is below the response threshold; monitor and leave service paths unchanged."

    tier_one_services = [name for name, attrs in result.nodes(data=True)
                         if attrs.get("role") == "primary" and attrs.get("tier") == 1]
    active_endpoints = []
    verification = {}
    for name in tier_one_services:
        endpoint = name + " Backup" if name == target and response_mode == "Failover" else name
        status = result.nodes[endpoint].get("status")
        available = (
            status in ("Active", "Active (failover)")
            or status.startswith("Safe fallback")
        ) and not result.nodes[endpoint].get("isolated")
        verification[name] = available
        if available:
            active_endpoints.append(endpoint)
    connected = all(nx.has_path(result, active_endpoints[0], endpoint)
                    for endpoint in active_endpoints[1:]) if active_endpoints else False
    critical_ok = all(verification.values()) and connected

    return result, {
        "service": target,
        "backup": backup,
        "tier": tier,
        "response_mode": response_mode,
        "response_detail": response_detail,
        "isolated": response_mode in ("Failover", "Isolation"),
        "rerouted": response_mode == "Failover",
        "risk_assessment": risk_assessment,
        "risk_score": risk_score,
        "critical_services_reachable": critical_ok,
        "verification": verification,
    }
