"""Identify tire stints from pit events."""
from __future__ import annotations

import pandas as pd


def segment_stints(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["driver", "lap"]).copy()
    df["stint_id"] = df.groupby("driver")["pit"].cumsum()
    return df
