"""Evaluate ABPWO pit lap predictions on synthetic data."""
from __future__ import annotations

import argparse
import numpy as np

from .bayesian_optimizer import optimize_pit_lap


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--circuit", default="bahrain")
    parser.add_argument("--season", type=int, default=2023)
    args = parser.parse_args()

    rng = np.random.default_rng(0)
    laps = np.arange(10, 40)
    true_opt = 25
    losses = (laps - true_opt) ** 2 + rng.normal(0, 5, size=len(laps))

    result = optimize_pit_lap(laps, losses)
    mae = abs(result.optimal_lap - true_opt)
    print(f"Circuit={args.circuit} season={args.season} predicted={result.optimal_lap} true={true_opt} MAE={mae:.2f}")


if __name__ == "__main__":
    main()
