"""Aggregate adjacency matrices from federated clients."""
from __future__ import annotations

import numpy as np


def aggregate_adjacency(matrices: list[np.ndarray]) -> np.ndarray:
    if not matrices:
        raise ValueError("No matrices to aggregate")
    stacked = np.stack(matrices, axis=0)
    return (stacked.mean(axis=0) > 0.5).astype(int)
