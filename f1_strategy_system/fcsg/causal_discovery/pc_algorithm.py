"""Simplified PC-like causal discovery.

This is a lightweight surrogate for the real PC algorithm. It builds a DAG
by adding edges between correlated variables, then orients edges based on
an ordering heuristic.
"""
from __future__ import annotations

import networkx as nx
import pandas as pd


def learn_dag(df: pd.DataFrame, nodes: list[str], corr_threshold: float = 0.25) -> nx.DiGraph:
    g = nx.DiGraph()
    g.add_nodes_from(nodes)

    corr = df[nodes].corr(numeric_only=True).fillna(0.0)
    for i, a in enumerate(nodes):
        for j, b in enumerate(nodes):
            if i >= j:
                continue
            if abs(corr.loc[a, b]) >= corr_threshold:
                # Orient using index order to keep acyclic
                g.add_edge(a, b) if i < j else g.add_edge(b, a)

    return g
