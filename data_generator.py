"""Generate deterministic synthetic traffic records for the city simulation."""
from __future__ import annotations

import numpy as np
import pandas as pd

SERVICES = ["Hospital", "Emergency Dispatch", "Traffic Control", "Water Supply", "Power Grid", "Public Display"]
SCENARIOS = ("Normal", "DoS", "Port Scan", "Malware-like")
FEATURES = ["packet_rate", "byte_rate", "failed_connections", "unique_ports", "cpu_load", "destination_count"]


def generate_traffic(
    rows: int = 1200,
    seed: int = 42,
    scenario: str | None = None,
    attack_fraction: float = 0.25,
    target_service: str | None = None,
) -> pd.DataFrame:
    """Return labeled synthetic traffic; selected incidents are mixed with normal traffic."""
    if rows < 1:
        raise ValueError("rows must be positive")
    rng = np.random.default_rng(seed)
    if scenario is not None and scenario not in SCENARIOS:
        raise ValueError("scenario must be one of: " + ", ".join(SCENARIOS))
    if not 0 < attack_fraction < 1:
        raise ValueError("attack_fraction must be between 0 and 1")
    if scenario is None:
        scenario_values = rng.choice(SCENARIOS, size=rows, p=[0.78, 0.08, 0.07, 0.07])
    elif scenario == "Normal":
        scenario_values = np.full(rows, "Normal", dtype=object)
    else:
        scenario_values = np.where(
            rng.random(rows) < attack_fraction, scenario, "Normal"
        )
    if target_service is not None and target_service not in SERVICES:
        raise ValueError("target_service must be one of: " + ", ".join(SERVICES))
    service = rng.choice(SERVICES, size=rows).astype(object)
    if target_service is not None:
        # Incident records come from the attacked service; normal records stay city-wide.
        service[scenario_values != "Normal"] = target_service
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
    # Attack effects overlap with the busy end of normal traffic, so some
    # incident records are hard to tell apart and the detector is not perfect.
    packet[dos] *= rng.uniform(1.2, 3.5, dos.sum())
    byte_rate[dos] *= rng.uniform(1.0, 2.0, dos.sum())
    cpu[dos] = (cpu[dos] + rng.uniform(5, 45, dos.sum())).clip(1, 99)
    failures[scan] += rng.integers(0, 12, scan.sum())
    ports[scan] += rng.integers(1, 25, scan.sum())
    destinations[scan] += rng.integers(0, 7, scan.sum())
    byte_rate[malware] *= rng.uniform(1.0, 1.7, malware.sum())
    failures[malware] += rng.integers(0, 7, malware.sum())
    cpu[malware] = (cpu[malware] + rng.uniform(5, 35, malware.sum())).clip(1, 99)
    return pd.DataFrame({
        "service": service, "packet_rate": packet.round(2), "byte_rate": byte_rate.round(2),
        "failed_connections": failures, "unique_ports": ports, "cpu_load": cpu.round(2),
        "destination_count": destinations, "scenario": scenario_values,
        "is_anomaly": (scenario_values != "Normal").astype(int),
    })
