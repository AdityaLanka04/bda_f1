"""Validate DAG with domain rules."""
from __future__ import annotations

import networkx as nx

FORBIDDEN_EDGES = {
    ("final_pos_delta", "pit_lap"),
    ("final_pos_delta", "tire_compound"),
}


def validate_dag(g: nx.DiGraph) -> nx.DiGraph:
    out = g.copy()
    for u, v in list(out.edges()):
        if (u, v) in FORBIDDEN_EDGES:
            out.remove_edge(u, v)
    # Ensure acyclic
    while not nx.is_directed_acyclic_graph(out):
        out.remove_edge(*list(out.edges())[0])
    return out
