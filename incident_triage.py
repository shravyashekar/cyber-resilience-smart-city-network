"""Turn Isolation Forest alerts into an incident decision for one city service.

This is the link between detection and response: the dashboard's selected
scenario only generates traffic, and the response is chosen from what the
detector actually flagged.
"""
import numpy as np

ALERT_RATE_THRESHOLD = 0.25   # share of the service's records flagged
MIN_ALERTS = 3                # ignore one or two stray false alarms

# Feature signature used to name the most likely threat type.
SIGNATURES = {
    "DoS": ["packet_rate", "byte_rate"],
    "Port Scan": ["unique_ports", "destination_count"],
    "Malware-like": ["failed_connections", "cpu_load"],
}
# Port scans and malware both raise failed connections; DoS and malware both
# raise CPU. Each signature therefore subtracts the features that separate it
# from the look-alike threat.
EXCLUDE = {
    "DoS": ["unique_ports"],
    "Port Scan": ["packet_rate"],
    "Malware-like": ["unique_ports", "packet_rate"],
}


def _z_scores(flagged, baseline):
    mean = baseline.mean(numeric_only=True)
    std = baseline.std(numeric_only=True).replace(0, 1)
    return (flagged.mean(numeric_only=True) - mean) / std


def triage_alerts(scored, service):
    """Decide whether the target service has an incident, and what kind.

    Records from other services act as the city's normal peer baseline.
    """
    target = scored[scored["service"] == service]
    peers = scored[scored["service"] != service]
    flagged = target[target["detected_anomaly"] == 1]
    records = int(len(target))
    alerts = int(len(flagged))
    alert_rate = alerts / records if records else 0.0
    incident = alerts >= MIN_ALERTS and alert_rate >= ALERT_RATE_THRESHOLD

    signature_scores = {}
    inferred = "Normal"
    if incident and len(peers):
        z = _z_scores(flagged, peers)
        for threat, features in SIGNATURES.items():
            score = float(np.mean([z[f] for f in features]))
            score -= 0.5 * float(np.mean([max(z[f], 0) for f in EXCLUDE[threat]]))
            signature_scores[threat] = round(score, 2)
        inferred = max(signature_scores, key=signature_scores.get)

    return {
        "service_records": records,
        "service_alerts": alerts,
        "alert_rate": alert_rate,
        "threshold": ALERT_RATE_THRESHOLD,
        "incident_detected": bool(incident),
        "inferred_threat": inferred,
        "signature_scores": signature_scores,
    }
