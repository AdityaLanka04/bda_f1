"""Bootstrap counterfactual simulations to estimate uncertainty bands."""
from __future__ import annotations

import numpy as np

from .scenario_replayer import replay


def quantify(intervention: dict, runs: int = 100) -> dict:
    positions = []
    for _ in range(runs):
        trace = replay(intervention)
        final = trace[-1]
        # Capture position of target car
        car_id = f"car_{intervention['car']}" if intervention["car"].isdigit() else f"car_{intervention['car']}"
        if car_id in final:
            positions.append(final[car_id]["position"])
    if not positions:
        return {"mean": None, "p10": None, "p90": None}
    arr = np.array(positions)
    return {
        "mean": float(arr.mean()),
        "p10": float(np.percentile(arr, 10)),
        "p90": float(np.percentile(arr, 90)),
    }
