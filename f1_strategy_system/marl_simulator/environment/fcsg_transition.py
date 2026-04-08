"""Causal transition model backed by FCSG.

This version uses a lightweight causal-inspired transition that factors
tire age, pit actions, and safety car to update position.
"""
from __future__ import annotations

import os
import random
from typing import Dict

import networkx as nx

from fcsg.causal_inference.circuit_fcsg import load_graph


class CausalTransitionModel:
    def __init__(self, model_path: str | None = None):
        self.graph = nx.DiGraph()
        if model_path and os.path.exists(model_path):
            self.graph = load_graph(model_path)

    def step(self, state: Dict, action: str) -> Dict:
        # Causal-inspired transition: pit actions trade position for fresh tires.
        next_state = dict(state)
        next_state["lap"] += 1
        next_state["tire_age"] += 1
        safety_car = int(next_state.get("safety_car", 0))
        track_temp = float(next_state.get("track_temp", 30.0))

        pit_penalty = 2 if action.startswith("pit") else 0
        tire_gain = 1 if next_state["tire_age"] <= 3 else 0
        temp_penalty = 1 if track_temp > 35.0 and next_state["compound"] == "soft" else 0

        if action.startswith("pit"):
            next_state["tire_age"] = 1
            next_state["compound"] = action.replace("pit_", "")

        # Safety car reduces position changes
        delta = (tire_gain - pit_penalty - temp_penalty)
        if safety_car:
            delta = 0
        else:
            # small stochasticity
            delta += 1 if random.random() < 0.15 else 0

        next_state["position"] = int(min(20, max(1, next_state["position"] - delta)))

        return next_state
