"""GP model utilities for ABPWO."""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass
class GPFit:
    model: object
    lap_min: float
    lap_max: float
    car_scale: float


def _make_features(laps: np.ndarray, car_id: float, lap_min: float, lap_max: float, car_scale: float) -> np.ndarray:
    laps = laps.astype(float)
    lap_range = max(lap_max - lap_min, 1.0)
    lap_norm = (laps - lap_min) / lap_range
    car_norm = (float(car_id) / car_scale) if car_scale > 0 else 0.0
    car_feat = np.full_like(lap_norm, car_norm)
    return np.stack([lap_norm, car_feat], axis=1)


def fit_gp(laps: np.ndarray, losses: np.ndarray, car_id: float = 0.0) -> GPFit | None:
    try:
        import torch
        from botorch.models import SingleTaskGP
        from botorch.fit import fit_gpytorch_mll
        from gpytorch.mlls.exact_marginal_log_likelihood import ExactMarginalLogLikelihood
        from botorch.models.transforms import Standardize
    except Exception:
        return None

    lap_min = float(laps.min())
    lap_max = float(laps.max())
    car_scale = max(float(car_id), 1.0)

    X = _make_features(laps, car_id, lap_min, lap_max, car_scale)
    Y = losses.astype(float)

    train_x = torch.tensor(X, dtype=torch.float32)
    train_y = torch.tensor(Y, dtype=torch.float32).unsqueeze(-1)

    model = SingleTaskGP(train_x, train_y, outcome_transform=Standardize(m=1))
    mll = ExactMarginalLogLikelihood(model.likelihood, model)
    fit_gpytorch_mll(mll)

    return GPFit(model=model, lap_min=lap_min, lap_max=lap_max, car_scale=car_scale)


def predict_gp(fit: GPFit, laps: np.ndarray, car_id: float = 0.0) -> tuple[np.ndarray, np.ndarray]:
    import torch

    X = _make_features(laps, car_id, fit.lap_min, fit.lap_max, fit.car_scale)
    x = torch.tensor(X, dtype=torch.float32)
    fit.model.eval()
    with torch.no_grad():
        posterior = fit.model.posterior(x)
        mean = posterior.mean.squeeze(-1).cpu().numpy()
        std = posterior.variance.sqrt().squeeze(-1).cpu().numpy()
    return mean, std
