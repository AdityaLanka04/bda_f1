"""Federated client stub for causal discovery."""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..causal_discovery.pc_algorithm import learn_dag
from ..nodes import NODES


def local_discovery(df: pd.DataFrame) -> np.ndarray:
    g = learn_dag(df, NODES)
    adj = np.zeros((len(NODES), len(NODES)), dtype=int)
    for u, v in g.edges():
        i = NODES.index(u)
        j = NODES.index(v)
        adj[i, j] = 1
    return adj
