"""Causal effect estimation.

Uses DoWhy if available, otherwise falls back to a difference-in-means estimate.
"""
from __future__ import annotations

import pandas as pd


def estimate_ate(df: pd.DataFrame, treatment: str, outcome: str, value: float) -> float:
    try:
        import dowhy
    except Exception:
        treated = df[df[treatment] == value][outcome]
        control = df[df[treatment] != value][outcome]
        if treated.empty or control.empty:
            return float("nan")
        return float(treated.mean() - control.mean())

    model = dowhy.CausalModel(
        data=df,
        treatment=treatment,
        outcome=outcome,
        common_causes=[c for c in df.columns if c not in (treatment, outcome)],
    )
    estimand = model.identify_effect()
    estimate = model.estimate_effect(estimand, method_name="backdoor.linear_regression")
    return float(estimate.value)
