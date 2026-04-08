"""Federated server stub to aggregate causal graphs."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .gradient_aggregator import aggregate_adjacency
from .fl_client import local_discovery
from ..nodes import NODES


def run_federated(clients: list[pd.DataFrame]) -> np.ndarray:
    matrices = [local_discovery(df) for df in clients]
    return aggregate_adjacency(matrices)


def adj_to_edges(adj: np.ndarray) -> list[tuple[str, str]]:
    edges = []
    for i, u in enumerate(NODES):
        for j, v in enumerate(NODES):
            if adj[i, j] == 1:
                edges.append((u, v))
    return edges
