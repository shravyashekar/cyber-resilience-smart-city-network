"""Generate deterministic synthetic traffic records for the city simulation."""
from __future__ import annotations

import numpy as np
import pandas as pd

SERVICES = ["Hospital", "Emergency Dispatch", "Traffic Control", "Water Supply", "Power Grid", "Public Display"]
SCENARIOS = ("Normal", "DoS", "Port Scan", "Malware-like")
FEATURES = ["packet_rate", "byte_rate", "failed_connections", "unique_ports", "cpu_load", "destination_count"]


def generate_traffic(rows: int = 1200, seed: int = 42, scenario: str | None = None) -> pd.DataFrame:
    """Return labeled, synthetic traffic records. No sockets or real traffic are used."""
    if rows < 1:
        raise ValueError("rows must be positive")
    rng = np.random.default_rng(seed)
    if scenario is not None and scenario not in SCENARIOS:
        raise ValueError("scenario must be one of: " + ", ".join(SCENARIOS))
    scenario_values = (np.full(rows, scenario, dtype=object) if scenario is not None else
                       rng.choice(SCENARIOS, size=rows, p=[0.78, 0.08, 0.07, 0.07]))
    service = rng.choice(SERVICES, size=rows)
    n = rows
    packet = rng.normal(120, 28, n).clip(5, None)
    byte_rate = rng.normal(85000, 18000, n).clip(500, None)
    failures = rng.poisson(1.0, n)
    ports = rng.poisson(2.0, n) + 1
    cpu = rng.normal(35, 12, n).clip(1, 99)
    destinations = rng.poisson(2.0, n) + 1
    dos = scenario_values == "DoS"
    scan = scenario_values == "Port Scan"
    malware = scenario_values == "Malware-like"
    packet[dos] *= rng.uniform(5, 11, dos.sum())
    byte_rate[dos] *= rng.uniform(2, 5, dos.sum())
    cpu[dos] = rng.uniform(75, 99, dos.sum())
    failures[scan] += rng.integers(12, 45, scan.sum())
    ports[scan] += rng.integers(25, 100, scan.sum())
    destinations[scan] += rng.integers(4, 18, scan.sum())
    byte_rate[malware] *= rng.uniform(1.5, 3, malware.sum())
    failures[malware] += rng.integers(4, 16, malware.sum())
    cpu[malware] = rng.uniform(65, 95, malware.sum())
    return pd.DataFrame({
        "service": service, "packet_rate": packet.round(2), "byte_rate": byte_rate.round(2),
        "failed_connections": failures, "unique_ports": ports, "cpu_load": cpu.round(2),
        "destination_count": destinations, "scenario": scenario_values,
        "is_anomaly": (scenario_values != "Normal").astype(int),
    })
