"""Lightweight refutation tests."""
from __future__ import annotations

import numpy as np
import pandas as pd


def placebo_treatment(df: pd.DataFrame, treatment: str, outcome: str) -> float:
    shuffled = df.copy()
    shuffled[treatment] = np.random.permutation(shuffled[treatment].values)
    return float(shuffled[treatment].corr(shuffled[outcome]))
