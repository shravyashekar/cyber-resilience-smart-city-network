"""Tier-aware simulated response actions for a fictional city network."""
import networkx as nx


def respond(graph, target, severity="High"):
    """Apply the PDF's tier policy: T1 failover, T2 safe fallback, T3 isolation."""
    if target not in graph or graph.nodes[target].get("role") == "backup":
        raise ValueError("Choose a primary city service")
    result = graph.copy()
    backup = target + " Backup"
    tier = result.nodes[target]["tier"]
    incident_edges = list(result.edges(target, data=True))

    if tier == 1:
        # Disconnect the affected device, then move its city links to its backup.
        neighbors = [(b if a == target else a, attrs) for a, b, attrs in incident_edges
                     if attrs.get("kind") == "service"]
        result.remove_edges_from([(a, b) for a, b, _ in incident_edges])
        result.nodes[target].update(status="Isolated (simulated)", isolated=True)
        result.nodes[backup].update(status="Active (failover)", role="active-backup")
        for neighbor, _attrs in neighbors:
            result.add_edge(backup, neighbor, kind="simulated-reroute")
        response_mode = "Failover"
        response_detail = "Tier 1 service isolated; backup activated and city links rerouted."
        score_base = 100
    elif tier == 2:
        # Keep the service connected in a restricted, simulated safe mode.
        result.nodes[target].update(status="Safe fallback (simulated)", isolated=False)
        result.nodes[backup].update(status="Standby (ready)", role="backup")
        response_mode = "Safe fallback"
        response_detail = "Tier 2 service continues in a restricted safe fallback mode."
        score_base = 70
    else:
        # Tier 3 is contained without activating its standby copy.
        result.remove_edges_from([(a, b) for a, b, _ in incident_edges])
        result.nodes[target].update(status="Isolated (simulated)", isolated=True)
        result.nodes[backup].update(status="Standby (ready)", role="backup")
        response_mode = "Isolation"
        response_detail = "Tier 3 service isolated; its backup remains on standby."
        score_base = 40

    severity_factor = {"Low": 0.55, "Medium": 0.7, "High": 0.85, "Critical": 1.0}.get(severity, 0.7)
    impact_score = round(score_base * severity_factor)

    tier_one_services = [name for name, attrs in result.nodes(data=True)
                         if attrs.get("role") == "primary" and attrs.get("tier") == 1]
    active_endpoints = []
    verification = {}
    for name in tier_one_services:
        endpoint = name + " Backup" if name == target and tier == 1 else name
        available = (result.nodes[endpoint].get("status") in ("Active", "Active (failover)")
                     and not result.nodes[endpoint].get("isolated"))
        verification[name] = available
        if available:
            active_endpoints.append(endpoint)
    connected = all(nx.has_path(result, active_endpoints[0], endpoint)
                    for endpoint in active_endpoints[1:]) if active_endpoints else False
    critical_ok = all(verification.values()) and connected
    return result, {
        "service": target, "backup": backup, "tier": tier, "response_mode": response_mode,
        "response_detail": response_detail, "isolated": tier in (1, 3),
        "rerouted": tier == 1, "impact_score": impact_score,
        "critical_services_reachable": critical_ok, "verification": verification,
    }
