"""Data cleaning utilities.

If PySpark is available, you can adapt this to distributed dataframes.
For now, we provide a pandas-based fallback for local runs.
"""
from __future__ import annotations

import pandas as pd


def clean_laps(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    # Remove obvious outliers (very slow laps)
    if "lap_time" in out.columns:
        out = out[out["lap_time"] < out["lap_time"].quantile(0.98)]
    return out.reset_index(drop=True)
