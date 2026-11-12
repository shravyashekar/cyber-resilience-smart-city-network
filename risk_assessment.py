"""Transparent risk scoring for the fictional smart-city services."""

SEVERITY_SCORES = {
    "None": 0,
    "Low": 25,
    "Medium": 50,
    "High": 75,
    "Critical": 100,
}
SCENARIO_SEVERITY = {
    "Normal": "None",
    "Port Scan": "Medium",
    "Malware-like": "High",
    "DoS": "Critical",
}
SERVICE_CRITICALITY = {1: 100, 2: 65, 3: 30}


def assess_risk(threat_severity, service_tier, civic_impact):
    """Return weighted risk components and a 0-100 score."""
    if threat_severity not in SEVERITY_SCORES:
        raise ValueError("Unknown threat severity")
    if service_tier not in SERVICE_CRITICALITY:
        raise ValueError("Service tier must be 1, 2, or 3")
    if not 0 <= civic_impact <= 100:
        raise ValueError("Civic impact must be between 0 and 100")

    severity_score = SEVERITY_SCORES[threat_severity]
    criticality_score = SERVICE_CRITICALITY[service_tier]
    risk_score = round(
        0.50 * severity_score + 0.25 * criticality_score + 0.25 * civic_impact
    )
    return {
        "threat_severity": threat_severity,
        "threat_severity_score": severity_score,
        "service_criticality_score": criticality_score,
        "civic_impact_score": civic_impact,
        "risk_score": risk_score,
    }
