"""Evaluate MARL simulator fidelity (placeholder)."""
from __future__ import annotations

import numpy as np


def kl_divergence(p: np.ndarray, q: np.ndarray) -> float:
    p = p / p.sum()
    q = q / q.sum()
    return float(np.sum(p * np.log((p + 1e-9) / (q + 1e-9))))


def main() -> None:
    # Dummy distributions
    p = np.array([0.2, 0.3, 0.5])
    q = np.array([0.25, 0.25, 0.5])
    print(f"KL divergence: {kl_divergence(p, q):.4f}")


if __name__ == "__main__":
    main()
