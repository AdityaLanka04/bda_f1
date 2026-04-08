"""End-to-end FCSG training script."""
from __future__ import annotations

import argparse
import os
import numpy as np
import pandas as pd
import networkx as nx

from .nodes import NODES
from .federated.fl_server import run_federated, adj_to_edges
from .causal_discovery.dag_validator import validate_dag
from .causal_inference.circuit_fcsg import save_graph


def _synthetic_df(n: int = 200) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    df = pd.DataFrame({
        "tire_compound": rng.integers(0, 3, size=n),
        "pit_lap": rng.integers(5, 50, size=n),
        "position_before": rng.integers(1, 20, size=n),
        "safety_car": rng.integers(0, 2, size=n),
        "track_temp": rng.normal(32, 4, size=n),
    })
    df["final_pos_delta"] = (
        -0.02 * df["pit_lap"] +
        -0.3 * df["position_before"] +
        0.5 * df["safety_car"] +
        rng.normal(0, 1, size=n)
    )
    return df


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--circuit", default="bahrain")
    parser.add_argument("--season", type=int, default=2023)
    parser.add_argument("--out", default="models/fcsg")
    args = parser.parse_args()

    # For prototype, synthesize per-team data and federate.
    clients = [_synthetic_df(150) for _ in range(5)]
    adj = run_federated(clients)
    g = nx.DiGraph()
    g.add_nodes_from(NODES)
    g.add_edges_from(adj_to_edges(adj))
    g = validate_dag(g)

    out_path = os.path.join(args.out, f"{args.circuit}_{args.season}.json")
    save_graph(g, out_path)
    print(f"Saved FCSG to {out_path}")


if __name__ == "__main__":
    main()
