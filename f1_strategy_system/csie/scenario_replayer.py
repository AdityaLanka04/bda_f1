"""Replay counterfactual scenarios via MARL simulator."""
from __future__ import annotations

from typing import Dict

from ..marl_simulator.simulate_race import simulate


def replay(intervention: Dict, model_path: str | None = None) -> list[dict]:
    # For prototype, run the simulator and inject intervention metadata.
    trace = simulate(model_path)
    for lap_state in trace:
        lap = next(iter(lap_state.values()))["lap"]
        if lap == intervention["lap"]:
            var = intervention.get("variable")
            if var == "pit_compound":
                car_id = f"car_{intervention['car']}" if str(intervention["car"]).isdigit() else f"car_{intervention['car']}"
                if car_id in lap_state:
                    lap_state[car_id]["compound"] = intervention["value"]
            elif var == "safety_car":
                for car in lap_state.values():
                    car["safety_car"] = int(intervention["value"])
            elif var == "track_temp":
                for car in lap_state.values():
                    car["track_temp"] = float(intervention["value"])
            elif var == "pit_lap":
                # Annotate target car with planned pit lap
                car_id = f"car_{intervention['car']}" if str(intervention["car"]).isdigit() else f"car_{intervention['car']}"
                if car_id in lap_state:
                    lap_state[car_id]["planned_pit_lap"] = int(intervention["value"])
    return trace
