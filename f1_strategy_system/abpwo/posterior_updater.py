"""Posterior updater for pit window optimization with persistence."""
from __future__ import annotations

import json
import os
import time
import numpy as np


class PitPosterior:
    def __init__(self, car_id: str | None = None):
        self.car_id = car_id
        self.laps: list[int] = []
        self.losses: list[float] = []
        self.updated_at = time.time()

    def update(self, lap: int, loss: float) -> None:
        self.laps.append(int(lap))
        self.losses.append(float(loss))
        self.updated_at = time.time()

    def as_arrays(self) -> tuple[np.ndarray, np.ndarray]:
        return np.array(self.laps), np.array(self.losses)

    def to_dict(self) -> dict:
        return {
            "car_id": self.car_id,
            "laps": self.laps,
            "losses": self.losses,
            "updated_at": self.updated_at,
        }

    @staticmethod
    def from_dict(payload: dict) -> "PitPosterior":
        obj = PitPosterior(car_id=payload.get("car_id"))
        obj.laps = list(payload.get("laps", []))
        obj.losses = list(payload.get("losses", []))
        obj.updated_at = float(payload.get("updated_at", time.time()))
        return obj

    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @staticmethod
    def load(path: str) -> "PitPosterior":
        with open(path, "r") as f:
            payload = json.load(f)
        return PitPosterior.from_dict(payload)


class PitPosteriorStore:
    def __init__(self):
        self._store: dict[str, PitPosterior] = {}

    def update(self, car_id: str, lap: int, loss: float) -> None:
        if car_id not in self._store:
            self._store[car_id] = PitPosterior(car_id=car_id)
        self._store[car_id].update(lap, loss)

    def get(self, car_id: str) -> PitPosterior | None:
        return self._store.get(car_id)

    def all(self) -> dict[str, PitPosterior]:
        return self._store

    def save_dir(self, path: str) -> None:
        os.makedirs(path, exist_ok=True)
        for car_id, post in self._store.items():
            post.save(os.path.join(path, f"{car_id}.json"))

    def load_dir(self, path: str) -> None:
        if not os.path.exists(path):
            return
        for name in os.listdir(path):
            if not name.endswith(".json"):
                continue
            car_id = name.replace(".json", "")
            self._store[car_id] = PitPosterior.load(os.path.join(path, name))
