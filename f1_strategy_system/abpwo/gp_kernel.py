"""Custom multi-output GP kernel (simplified)."""
from __future__ import annotations

import numpy as np


def rbf_kernel(x: np.ndarray, y: np.ndarray, length_scale: float = 5.0) -> np.ndarray:
    x = x[:, None]
    y = y[None, :]
    return np.exp(-0.5 * ((x - y) ** 2) / (length_scale ** 2))


def multi_car_kernel(laps: np.ndarray, car_corr: float = 0.2) -> np.ndarray:
    base = rbf_kernel(laps, laps)
    return base * (1.0 + car_corr)
