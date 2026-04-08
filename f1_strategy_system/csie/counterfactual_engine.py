"""Execute counterfactual queries using FCSG.

This module prefers real FastF1 race data and builds a lap-level causal table
with safety-car flags and weather covariates. It falls back to synthetic data
if FastF1 data is unavailable.
"""
from __future__ import annotations

import argparse
import logging
import os
import warnings
from typing import Tuple

# Avoid noisy matplotlib/font cache warnings in restricted environments.
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp")

import numpy as np
import pandas as pd

from .nl_parser.query_parser import parse_query
from fcsg.causal_inference.dowhy_estimator import estimate_ate

COMPOUND_TO_ID = {"soft": 0, "medium": 1, "hard": 2, "inter": 3, "wet": 4}


def _synthetic_df() -> pd.DataFrame:
    rng = np.random.default_rng(1)
    drivers = [
        ("VER", "1"),
        ("PER", "11"),
        ("LEC", "16"),
        ("SAI", "55"),
        ("HAM", "44"),
        ("RUS", "63"),
        ("NOR", "4"),
        ("ALO", "14"),
    ]
    idx = rng.integers(0, len(drivers), size=200)
    driver_code = [drivers[i][0] for i in idx]
    car_number = [drivers[i][1] for i in idx]
    df = pd.DataFrame({
        "driver_code": driver_code,
        "car_number": car_number,
        "driver_id": idx,
        "lap_number": rng.integers(1, 58, size=200),
        "pit_compound": rng.integers(0, 3, size=200),
        "pit_lap": rng.integers(5, 50, size=200),
        "safety_car": rng.integers(0, 2, size=200),
        "track_temp": rng.normal(32, 4, size=200),
        "position": rng.integers(1, 21, size=200),
        "lap_time_sec": rng.normal(92, 3, size=200),
    })
    df["final_pos_delta"] = (
        -0.02 * df["pit_lap"] +
        0.5 * df["safety_car"] +
        rng.normal(0, 1, size=200)
    )
    return df


def _configure_fastf1_logging() -> None:
    """Reduce noisy FastF1 logs in API mode.

    Set env FASTF1_LOG_LEVEL to DEBUG/INFO/WARNING/ERROR to override.
    """
    level = os.getenv("FASTF1_LOG_LEVEL", "ERROR")
    try:
        import fastf1

        fastf1.set_log_level(level)
    except Exception:
        return

    # Prevent duplicate records via root/uvicorn handlers.
    logger_names = [
        "fastf1",
        "fastf1.api",
        "fastf1.core",
        "fastf1.req",
        "fastf1.ergast",
        "fastf1.fastf1.core",
        "fastf1.fastf1.req",
    ]
    for name in logger_names:
        lg = logging.getLogger(name)
        if lg.handlers:
            lg.propagate = False


def _disable_fastf1_cache_hard() -> None:
    """Disable FastF1 caching (including default auto-cache path creation)."""
    try:
        import fastf1
        import fastf1.req as ffreq

        # Disable cache usage for request path.
        fastf1.Cache.set_disabled()
        ffreq.Cache._tmp_disabled = True

        # Prevent auto-enabling default cache folder on every GET.
        ffreq.Cache._default_cache_enabled = True
        ffreq.Cache._CACHE_DIR = None

        # Drop any previously created cached session.
        cached_session = getattr(ffreq.Cache, "_requests_session_cached", None)
        if cached_session is not None:
            try:
                cached_session.close()
            except Exception:
                pass
            ffreq.Cache._requests_session_cached = None
    except Exception:
        # If FastF1 internals change, continue without hard-fail.
        return


def _safe_float(v, default: float = 0.0) -> float:
    try:
        if pd.isna(v):
            return default
        return float(v)
    except Exception:
        return default


def _safe_int(v, default: int = 0) -> int:
    try:
        if pd.isna(v):
            return default
        return int(v)
    except Exception:
        return default


def _is_safety_car(track_status) -> int:
    """Detect safety-car phases from FIA track-status codes.

    FastF1 stores TrackStatus as strings containing status digits.
    Safety car is encoded with '4'. We treat missing as 0.
    """
    if track_status is None or (isinstance(track_status, float) and np.isnan(track_status)):
        return 0
    s = str(track_status)
    return 1 if "4" in s else 0


def _merge_weather_for_laps(laps: pd.DataFrame, weather: pd.DataFrame | None) -> pd.DataFrame:
    out = laps.copy()
    if weather is None or weather.empty:
        out["track_temp"] = 0.0
        out["air_temp"] = 0.0
        out["humidity"] = 0.0
        out["wind_speed"] = 0.0
        out["rainfall"] = 0.0
        return out

    # Align by session-relative time using nearest previous weather sample.
    if "Time" not in weather.columns or "Time" not in out.columns:
        out["track_temp"] = _safe_float(weather["TrackTemp"].mean(), 0.0) if "TrackTemp" in weather.columns else 0.0
        out["air_temp"] = _safe_float(weather["AirTemp"].mean(), 0.0) if "AirTemp" in weather.columns else 0.0
        out["humidity"] = _safe_float(weather["Humidity"].mean(), 0.0) if "Humidity" in weather.columns else 0.0
        out["wind_speed"] = _safe_float(weather["WindSpeed"].mean(), 0.0) if "WindSpeed" in weather.columns else 0.0
        out["rainfall"] = 1.0 if ("Rainfall" in weather.columns and weather["Rainfall"].astype(bool).any()) else 0.0
        return out

    lw = weather.copy().sort_values("Time")
    ll = out.copy().sort_values("Time")
    merged = pd.merge_asof(
        ll,
        lw[["Time"] + [c for c in ["TrackTemp", "AirTemp", "Humidity", "WindSpeed", "Rainfall"] if c in lw.columns]],
        on="Time",
        direction="backward",
    )
    merged["track_temp"] = merged["TrackTemp"].map(lambda x: _safe_float(x, 0.0)) if "TrackTemp" in merged.columns else 0.0
    merged["air_temp"] = merged["AirTemp"].map(lambda x: _safe_float(x, 0.0)) if "AirTemp" in merged.columns else 0.0
    merged["humidity"] = merged["Humidity"].map(lambda x: _safe_float(x, 0.0)) if "Humidity" in merged.columns else 0.0
    merged["wind_speed"] = merged["WindSpeed"].map(lambda x: _safe_float(x, 0.0)) if "WindSpeed" in merged.columns else 0.0
    if "Rainfall" in merged.columns:
        merged["rainfall"] = merged["Rainfall"].astype(bool).astype(int)
    else:
        merged["rainfall"] = 0
    return merged


def _fastf1_dataset(season: int, event: str) -> Tuple[pd.DataFrame, str]:
    """Build a lap-level dataset from FastF1.

    Returns (df, source_label). Raises on failure.
    """
    import fastf1
    _disable_fastf1_cache_hard()
    _configure_fastf1_logging()

    session = fastf1.get_session(season, event, "R")
    session.load(laps=True, telemetry=False, weather=True)

    laps = session.laps.copy()
    results = session.results

    weather = None
    try:
        weather = session.weather_data
    except Exception:
        weather = None

    laps = _merge_weather_for_laps(laps, weather)

    data_rows = []
    drivers = sorted([str(d) for d in laps["Driver"].dropna().unique()])
    if not drivers:
        raise RuntimeError("No drivers found in FastF1 laps data")

    for driver_idx, driver in enumerate(drivers):
        driver_laps = laps[laps["Driver"] == driver].copy()
        if driver_laps.empty:
            continue

        # First pit lap
        pit_lap = None
        pit_rows = driver_laps[driver_laps["PitInTime"].notna()]
        if not pit_rows.empty:
            pit_lap = int(pit_rows["LapNumber"].min())
        if pit_lap is None:
            pit_lap = int(driver_laps["LapNumber"].max())

        # Prefer official results, but fall back to lap-derived positions when unavailable.
        grid = None
        pos = None
        if results is not None and not results.empty:
            try:
                mask = pd.Series(False, index=results.index)
                if "Abbreviation" in results.columns:
                    mask = mask | (results["Abbreviation"].astype(str) == driver)
                if "DriverCode" in results.columns:
                    mask = mask | (results["DriverCode"].astype(str) == driver)
                rr = results[mask]
                if not rr.empty:
                    r0 = rr.iloc[0]
                    grid = _safe_int(r0.get("GridPosition"), default=0)
                    pos = _safe_int(r0.get("Position"), default=0)
            except Exception:
                grid, pos = None, None

        if not grid or not pos:
            first_pos = _safe_int(driver_laps.sort_values("LapNumber").iloc[0].get("Position"), default=0)
            last_pos = _safe_int(driver_laps.sort_values("LapNumber").iloc[-1].get("Position"), default=0)
            grid = first_pos if first_pos > 0 else 20
            pos = last_pos if last_pos > 0 else 20

        finish_position = pos

        for _, lap in driver_laps.iterrows():
            compound = str(lap.get("Compound", "soft")).lower()
            pit_compound_id = COMPOUND_TO_ID.get(compound, 0)
            lap_num = _safe_int(lap.get("LapNumber"), 0)
            is_pit_lap = 1 if not pd.isna(lap.get("PitInTime")) else 0
            current_pos = _safe_int(lap.get("Position"), 20)
            data_rows.append({
                "driver_id": driver_idx,
                "driver_code": driver,
                "car_number": str(lap.get("DriverNumber")) if not pd.isna(lap.get("DriverNumber")) else "",
                "lap_number": lap_num,
                "pit_lap": pit_lap,
                "pit_now": is_pit_lap,
                "pit_compound": pit_compound_id,
                "tire_age": _safe_float(lap.get("TyreLife"), 0.0),
                "stint": _safe_int(lap.get("Stint"), 0),
                "position": current_pos,
                "lap_time_sec": _safe_float(lap["LapTime"].total_seconds(), 0.0) if hasattr(lap.get("LapTime"), "total_seconds") else _safe_float(lap.get("LapTime"), 0.0),
                "safety_car": _is_safety_car(lap.get("TrackStatus")),
                "track_temp": _safe_float(lap.get("track_temp"), 0.0),
                "air_temp": _safe_float(lap.get("air_temp"), 0.0),
                "humidity": _safe_float(lap.get("humidity"), 0.0),
                "wind_speed": _safe_float(lap.get("wind_speed"), 0.0),
                "rainfall": _safe_int(lap.get("rainfall"), 0),
                # Lap-level outcome: potential places gained from this lap to finish.
                "final_pos_delta": current_pos - finish_position,
            })

    if not data_rows:
        raise RuntimeError("No driver rows produced from FastF1")

    df = pd.DataFrame(data_rows).dropna(subset=["final_pos_delta"])
    return df, f"FastF1 {event} {season}"


def _is_lap_level_df(df: pd.DataFrame) -> bool:
    required = {
        "driver_code",
        "car_number",
        "pit_compound",
        "pit_lap",
        "safety_car",
        "track_temp",
        "final_pos_delta",
        "lap_number",
        "position",
        "lap_time_sec",
    }
    return required.issubset(set(df.columns))


def load_real_or_synth(season: int, event: str) -> Tuple[pd.DataFrame, str]:
    """Load FastF1-based dataset if possible, else fall back to synthetic.

    Caching is intentionally disabled to avoid stale repeated results.
    """
    try:
        return _fastf1_dataset(season, event)
    except Exception:
        return _synthetic_df(), "synthetic"


def _human_explanation(
    intervention: dict,
    ate: float,
    source: str,
    n: int,
    global_ate: float | None = None,
    per_car_ate: float | None = None,
    conditioned: bool = False,
) -> str:
    var = intervention["variable"]
    val = intervention["value"]
    lap = intervention["lap"]
    car = intervention["car"]

    if var == "pit_compound":
        sentence = f"Set car {car} to {val} tires on lap {lap}."
    elif var == "pit_lap":
        sentence = f"Change car {car}'s pit lap to {val} (applied at lap {lap})."
    elif var == "safety_car":
        sentence = f"Safety car set to {val} on lap {lap}."
    elif var == "track_temp":
        sentence = f"Track temperature set to {val}°C on lap {lap}."
    else:
        sentence = f"Apply intervention {var}={val} on lap {lap}."

    if ate is None or np.isnan(ate):
        direction = "could not be estimated for"
        ate_text = "unavailable"
    elif abs(ate) < 1e-3:
        direction = "has no clear effect on"
        ate_text = f"{ate:.3f}"
    else:
        direction = "improves" if ate > 0 else "worsens"
        ate_text = f"{ate:.3f}"
    summary = (
        f"{sentence} Estimated causal effect on final_pos_delta is {ate_text}, "
        f"which {direction} finishing position (positive = gain). "
        f"Data source: {source} (rows={n}, lap-level covariates + real safety-car flags when available)."
    )
    if conditioned:
        g = "nan" if global_ate is None or np.isnan(global_ate) else f"{global_ate:.3f}"
        p = "nan" if per_car_ate is None or np.isnan(per_car_ate) else f"{per_car_ate:.3f}"
        summary += f" Global ATE={g}; per-car ATE={p}."
    return summary


def _build_binary_intervention(df: pd.DataFrame, treatment: str, value, intervention_lap: int | None = None) -> pd.DataFrame:
    out = df.copy()
    if treatment not in out.columns:
        raise ValueError(f"Treatment '{treatment}' not found in dataset")

    lap_gate = np.ones(len(out), dtype=bool)
    if intervention_lap is not None and "lap_number" in out.columns:
        if treatment in {"safety_car", "track_temp"}:
            lap_gate = (out["lap_number"] - int(intervention_lap)).abs() <= 1
        else:
            lap_gate = out["lap_number"] >= int(intervention_lap)

    if treatment == "track_temp":
        # Use threshold intervention for continuous variable.
        out["_intervention_T"] = ((out[treatment] >= float(value)) & lap_gate).astype(int)
    else:
        out["_intervention_T"] = ((out[treatment] == value) & lap_gate).astype(int)
    return out


def _contrast_counts(df: pd.DataFrame) -> dict:
    treated = int((df["_intervention_T"] == 1).sum()) if "_intervention_T" in df.columns else 0
    control = int((df["_intervention_T"] == 0).sum()) if "_intervention_T" in df.columns else 0
    return {"treated_rows": treated, "control_rows": control}


def _estimate_binary_ate(df: pd.DataFrame) -> float:
    if "_intervention_T" not in df.columns:
        raise ValueError("Missing binary treatment column")
    if df["_intervention_T"].nunique() < 2:
        return float("nan")
    if "final_pos_delta" not in df.columns:
        return float("nan")
    # Guard against degenerate subsets where regression is not identifiable.
    if float(df["final_pos_delta"].std(ddof=0)) < 1e-12:
        return float("nan")

    model_df = df.copy()
    # Avoid dowhy/sklearn one-hot incompatibility by numeric encoding.
    for col in model_df.columns:
        if model_df[col].dtype == "object":
            model_df[col] = pd.factorize(model_df[col])[0]

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message=r".*Series.__getitem__ treating keys as positions is deprecated.*",
            category=FutureWarning,
        )
        warnings.filterwarnings(
            "ignore",
            category=RuntimeWarning,
            module=r"statsmodels\..*",
        )
        warnings.filterwarnings(
            "ignore",
            category=RuntimeWarning,
            module=r"numpy\..*",
        )
        warnings.filterwarnings(
            "ignore",
            message=r".*divide by zero encountered in scalar divide.*",
            category=RuntimeWarning,
        )
        return estimate_ate(model_df, "_intervention_T", "final_pos_delta", 1)


def _subset_for_car(df: pd.DataFrame, car: str) -> tuple[pd.DataFrame, bool]:
    token = str(car).strip().upper()
    if token == "RACE":
        return df, False

    mask = pd.Series(False, index=df.index)
    if "driver_code" in df.columns:
        mask = mask | (df["driver_code"].astype(str).str.upper() == token)
    if token.isdigit() and "car_number" in df.columns:
        normalized = str(int(token))
        mask = mask | (df["car_number"].astype(str) == normalized)

    subset = df[mask].copy()
    if subset.empty:
        return df, False
    return subset, True


def _safe_num(v):
    try:
        f = float(v)
        if np.isnan(f):
            return None
        return f
    except Exception:
        return None


def run_counterfactual(query: str, season: int = 2023, event: str = "Bahrain") -> dict:
    intervention = parse_query(query)
    df, source = load_real_or_synth(season, event)

    treatment = intervention.variable
    value = intervention.value
    if treatment == "pit_compound":
        value = COMPOUND_TO_ID.get(str(value).lower(), 0)
    elif treatment == "pit_lap":
        value = int(value)
    elif treatment == "safety_car":
        value = int(value)
    elif treatment == "track_temp":
        value = float(value)
    elif treatment == "strategy_label":
        treatment = "pit_lap"
        value = int(intervention.lap)

    # Global intervention effect
    intervention_lap = int(intervention.lap) if getattr(intervention, "lap", None) is not None else None
    global_df = _build_binary_intervention(df, treatment, value, intervention_lap=intervention_lap)
    global_ate = _estimate_binary_ate(global_df)
    global_contrast = _contrast_counts(global_df)

    # Per-car intervention effect when query targets a specific car/driver.
    car_df, conditioned = _subset_for_car(df, intervention.car)
    per_car_ate = None
    per_car_contrast = None
    if conditioned:
        local_df = _build_binary_intervention(car_df, treatment, value, intervention_lap=intervention_lap)
        per_car_ate = _estimate_binary_ate(local_df)
        per_car_contrast = _contrast_counts(local_df)

    # Keep backward-compatible "ate" while adding explicit global/per-car fields.
    primary_ate = per_car_ate if per_car_ate is not None and not np.isnan(per_car_ate) else global_ate
    primary_ate_safe = _safe_num(primary_ate)
    explanation = _human_explanation(
        intervention.model_dump(),
        primary_ate if primary_ate is not None else float("nan"),
        source,
        len(df),
        global_ate=global_ate,
        per_car_ate=per_car_ate,
        conditioned=conditioned,
    )

    return {
        "intervention": intervention.model_dump(),
        "ate": primary_ate_safe,
        "global_ate": _safe_num(global_ate),
        "per_car_ate": _safe_num(per_car_ate),
        "conditioning": {
            "requested_car": intervention.car,
            "applied": conditioned,
            "subset_rows": int(len(car_df)) if conditioned else None,
        },
        "contrast": {
            "global": global_contrast,
            "per_car": per_car_contrast,
        },
        "explanation": explanation,
        "data_source": source,
        "sample_size": len(df),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    parser.add_argument("--season", type=int, default=2023)
    parser.add_argument("--event", type=str, default="Bahrain")
    args = parser.parse_args()

    result = run_counterfactual(args.query, season=args.season, event=args.event)
    print(result)


if __name__ == "__main__":
    main()
