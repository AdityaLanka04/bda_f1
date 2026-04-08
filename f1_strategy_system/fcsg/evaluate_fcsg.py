"""Evaluate FCSG edge recovery on synthetic ground truth."""
from __future__ import annotations

import argparse
import os
import networkx as nx

from .causal_inference.circuit_fcsg import load_graph

TRUE_EDGES = {
    ("pit_lap", "final_pos_delta"),
    ("position_before", "final_pos_delta"),
    ("safety_car", "final_pos_delta"),
}


def precision_recall(pred_edges: set[tuple[str, str]]) -> tuple[float, float]:
    tp = len(pred_edges & TRUE_EDGES)
    fp = len(pred_edges - TRUE_EDGES)
    fn = len(TRUE_EDGES - pred_edges)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return precision, recall


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="models/fcsg/bahrain_2023.json")
    args = parser.parse_args()

    if not os.path.exists(args.model):
        raise SystemExit(f"Model not found: {args.model}")
    g = load_graph(args.model)
    pred_edges = set(g.edges())
    p, r = precision_recall(pred_edges)
    print(f"Edge precision={p:.2f}, recall={r:.2f}")


if __name__ == "__main__":
    main()
