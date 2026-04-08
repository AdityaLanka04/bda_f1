"""Bayesian pit window optimizer with uncertainty bands.

Uses BoTorch/GPyTorch if available; otherwise falls back to a quadratic fit.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass
class OptimizationResult:
    optimal_lap: int
    mean: float
    std: float
    method: str


def _fallback(laps: np.ndarray, lap_loss: np.ndarray) -> OptimizationResult:
    if len(laps) < 3:
        idx = int(np.argmin(lap_loss))
        return OptimizationResult(int(laps[idx]), float(lap_loss[idx]), 0.0, "argmin")
    coeffs = np.polyfit(laps, lap_loss, deg=2)
    a, b, c = coeffs
    if abs(a) < 1e-6:
        idx = int(np.argmin(lap_loss))
        return OptimizationResult(int(laps[idx]), float(lap_loss[idx]), 0.0, "argmin")
    opt = -b / (2 * a)
    opt_lap = int(np.clip(round(opt), laps.min(), laps.max()))
    est = float(a * opt ** 2 + b * opt + c)
    return OptimizationResult(opt_lap, est, 0.0, "quadratic")


def optimize_pit_lap(
    laps: np.ndarray,
    lap_loss: np.ndarray,
    car_id: float | None = None,
    lap_min: int | None = None,
    lap_max: int | None = None,
) -> OptimizationResult:
    laps = np.asarray(laps, dtype=float)
    lap_loss = np.asarray(lap_loss, dtype=float)
    if laps.shape[0] != lap_loss.shape[0]:
        raise ValueError("laps and lap_loss length mismatch")
    if laps.size == 0:
        raise ValueError("empty lap list")

    lap_min = int(lap_min) if lap_min is not None else int(laps.min())
    lap_max = int(lap_max) if lap_max is not None else int(laps.max())
    lap_min, lap_max = min(lap_min, lap_max), max(lap_min, lap_max)
    car_id = float(car_id) if car_id is not None else 0.0

    if len(laps) < 6:
        return _fallback(laps, lap_loss)

    try:
        from .gp_model import fit_gp, predict_gp
        fit = fit_gp(laps, lap_loss, car_id=car_id)
        if fit is None:
            return _fallback(laps, lap_loss)
        grid = np.arange(lap_min, lap_max + 1)
        mean, std = predict_gp(fit, grid, car_id=car_id)
        idx = int(np.argmin(mean))
        return OptimizationResult(int(grid[idx]), float(mean[idx]), float(std[idx]), "gp")
    except Exception:
        return _fallback(laps, lap_loss)
