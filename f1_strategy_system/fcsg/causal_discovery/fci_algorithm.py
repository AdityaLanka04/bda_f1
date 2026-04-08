"""FCI placeholder.

In this prototype we reuse the simplified PC routine as a stand-in.
"""
from __future__ import annotations

import pandas as pd
import networkx as nx

from .pc_algorithm import learn_dag


def learn_dag_with_latents(df: pd.DataFrame, nodes: list[str]) -> nx.DiGraph:
    return learn_dag(df, nodes, corr_threshold=0.2)
