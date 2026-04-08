"""Feature engineering for lap-level data."""
from __future__ import annotations

import pandas as pd


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["lap_idx"] = out["lap"].astype(int)
    out["tire_age"] = out.groupby(["driver", "stint_id"]).cumcount() + 1
    out["tire_life_ratio"] = out["tire_age"] / out.groupby("driver")["lap"].transform("max")
    return out
