"""Emergency re-optimization when safety car appears."""
from __future__ import annotations

from typing import Dict

from .bayesian_optimizer import optimize_pit_lap
from .posterior_updater import PitPosterior


def recompute_all(posteriors: Dict[str, PitPosterior]) -> Dict[str, int]:
    out = {}
    for car, post in posteriors.items():
        laps, losses = post.as_arrays()
        if len(laps) < 3:
            out[car] = int(laps[-1]) if len(laps) else 0
        else:
            out[car] = optimize_pit_lap(laps, losses).optimal_lap
    return out
