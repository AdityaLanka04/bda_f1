"""Rule-based labeling of pit strategy events."""
from __future__ import annotations

import pandas as pd


def label_strategies(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["strategy_label"] = "normal"
    # Simple heuristic: early pit = undercut, late pit = overcut
    if "lap" in out.columns:
        median_lap = out["lap"].median()
        out.loc[(out["pit"] == 1) & (out["lap"] <= median_lap), "strategy_label"] = "undercut"
        out.loc[(out["pit"] == 1) & (out["lap"] > median_lap), "strategy_label"] = "overcut"
    return out
