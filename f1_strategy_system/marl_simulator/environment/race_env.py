"""Multi-agent race environment with Gym-style API."""
from __future__ import annotations

import random
from typing import Dict

from .action_space import ACTIONS
from .fcsg_transition import CausalTransitionModel


class RaceEnv:
    def __init__(self, num_cars: int = 20, model_path: str | None = None, max_laps: int = 57):
        self.num_cars = num_cars
        self.max_laps = max_laps
        self.transition = CausalTransitionModel(model_path)
        self._init_spaces()
        self.reset()

    def _init_spaces(self) -> None:
        try:
            import gymnasium as gym
            from gymnasium import spaces
        except Exception:
            self.observation_space = None
            self.action_space = None
            return
        self.observation_space = spaces.Box(low=0.0, high=1.0, shape=(4,), dtype=float)
        self.action_space = spaces.Discrete(len(ACTIONS))

    def _obs(self, state: dict) -> list[float]:
        compound_map = {"soft": 0, "medium": 1, "hard": 2, "inter": 3, "wet": 4}
        return [
            state["lap"] / max(self.max_laps, 1),
            state["tire_age"] / max(self.max_laps, 1),
            compound_map.get(state["compound"], 0) / 4.0,
            state["position"] / max(self.num_cars, 1),
        ]

    def reset(self, seed: int | None = None, options: dict | None = None):
        self.lap = 0
        self.state = {
            f"car_{i+1}": {
                "lap": 0,
                "tire_age": 1,
                "compound": "soft",
                "position": i + 1,
            }
            for i in range(self.num_cars)
        }
        obs = {car: self._obs(s) for car, s in self.state.items()}
        info = {car: {} for car in self.state.keys()}
        return obs, info

    def step(self, actions: Dict[str, str]):
        self.lap += 1
        next_state = {}
        for car, action in actions.items():
            next_state[car] = self.transition.step(self.state[car], action)
        self.state = next_state
        terminated = self.lap >= self.max_laps
        rewards = {car: 0.0 for car in self.state.keys()}
        obs = {car: self._obs(s) for car, s in self.state.items()}
        terminateds = {car: terminated for car in self.state.keys()}
        terminateds["__all__"] = terminated
        truncateds = {car: False for car in self.state.keys()}
        truncateds["__all__"] = False
        infos = {car: {} for car in self.state.keys()}
        return obs, rewards, terminateds, truncateds, infos

    def sample_action(self) -> str:
        return random.choice(ACTIONS)
