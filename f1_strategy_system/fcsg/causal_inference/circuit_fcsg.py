"""Utility to store per-circuit causal graphs."""
from __future__ import annotations

import json
import os
from typing import Dict

import networkx as nx


def save_graph(g: nx.DiGraph, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = {
        "nodes": list(g.nodes()),
        "edges": list(g.edges()),
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_graph(path: str) -> nx.DiGraph:
    with open(path, "r") as f:
        data: Dict = json.load(f)
    g = nx.DiGraph()
    g.add_nodes_from(data["nodes"])
    g.add_edges_from(data["edges"])
    return g
