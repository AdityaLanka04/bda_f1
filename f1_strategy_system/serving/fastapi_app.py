"""Main API gateway for FCSG, ABPWO, MARL-RS, and CSIE."""
from __future__ import annotations

import math
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Allow running as script or module
if __package__ in (None, ""):
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from fcsg.causal_inference.dowhy_estimator import estimate_ate
from abpwo.bayesian_optimizer import optimize_pit_lap
from marl_simulator.simulate_race import simulate
from csie.counterfactual_engine import COMPOUND_TO_ID, load_real_or_synth, run_counterfactual

app = FastAPI(title="F1 Strategy System")

# Dev CORS: allow dashboard (Vite) to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def disable_client_cache(request, call_next):
    """Force clients/proxies to fetch fresh responses every request."""
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


class ATERequest(BaseModel):
    treatment: str = "safety_car"
    outcome: str = "final_pos_delta"
    value: str | int | float = 1
    season: int | None = 2024
    event: str | None = "Monza"
    car: str | None = None


class PitWindowRequest(BaseModel):
    laps: list[int] = Field(default_factory=list)
    losses: list[float] = Field(default_factory=list)
    car_id: str | None = None
    season: int | None = 2024
    event: str | None = "Monza"
    lap_min: int | None = None
    lap_max: int | None = None


class SimRequest(BaseModel):
    model_config = {"protected_namespaces": ()}
    model_path: str | None = None
    checkpoint_path: str | None = None
    season: int | None = 2024
    event: str | None = "Monza"
    max_laps: int | None = None


class CFRequest(BaseModel):
    query: str
    season: int | None = 2023
    event: str | None = "Bahrain"


@app.get("/health")
def health():
    return {"status": "ok"}


def _safe_float(v):
    try:
        f = float(v)
        if math.isnan(f) or math.isinf(f):
            return None
        return f
    except Exception:
        return None


def _subset_by_car(df, car: str | None):
    import pandas as pd

    if not car:
        return df
    token = str(car).strip().upper()
    if token in {"", "RACE"}:
        return df
    mask = pd.Series(False, index=df.index)
    if "driver_code" in df.columns:
        mask = mask | (df["driver_code"].astype(str).str.upper() == token)
    if token.isdigit() and "car_number" in df.columns:
        normalized = str(int(token))
        mask = mask | (df["car_number"].astype(str) == normalized)
    subset = df[mask].copy()
    return subset if not subset.empty else df


def _normalize_treatment_and_value(df, treatment: str, value):
    tr = treatment.strip().lower()
    if tr in {"pit", "pit_now"} and "pit_now" in df.columns:
        return "pit_now", int(value)
    if tr in {"pit_lap", "pitlap"} and "pit_lap" in df.columns:
        return "pit_lap", int(value)
    if tr in {"pit_compound", "compound"} and "pit_compound" in df.columns:
        if isinstance(value, str):
            return "pit_compound", COMPOUND_TO_ID.get(value.lower(), 0)
        return "pit_compound", int(value)
    if tr in {"safety_car", "sc"} and "safety_car" in df.columns:
        return "safety_car", int(value)
    if tr in {"track_temp", "temperature"} and "track_temp" in df.columns:
        return "track_temp", float(value)
    if treatment in df.columns:
        return treatment, value
    raise ValueError(f"Unknown treatment '{treatment}' for available columns")


def _normalize_outcome(df, outcome: str):
    if outcome in df.columns:
        return outcome
    aliases = {
        "position_delta": "final_pos_delta",
        "lap_time": "lap_time_sec",
        "lap_time_seconds": "lap_time_sec",
    }
    mapped = aliases.get(outcome)
    if mapped and mapped in df.columns:
        return mapped
    raise ValueError(f"Unknown outcome '{outcome}' for available columns")


@app.post("/fcsg/ate")
def fcsg_ate(req: ATERequest):
    try:
        season = req.season or 2024
        event = req.event or "Monza"
        df, source = load_real_or_synth(season, event)
        df = _subset_by_car(df, req.car)
        treatment, value = _normalize_treatment_and_value(df, req.treatment, req.value)
        outcome = _normalize_outcome(df, req.outcome)
        model_df = df[[c for c in df.columns if c not in {"driver_code", "car_number"}]].copy()
        ate = estimate_ate(model_df, treatment, outcome, value)
        return {
            "ate": _safe_float(ate),
            "treatment": treatment,
            "value": value,
            "outcome": outcome,
            "sample_size": int(len(df)),
            "data_source": source,
            "season": season,
            "event": event,
            "car_scope": req.car or "RACE",
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc


def _abpwo_inputs_from_data(df):
    if "pit_now" in df.columns and int(df["pit_now"].sum()) >= 3:
        grouped = (
            df[df["pit_now"] == 1]
            .groupby("lap_number", as_index=True)["final_pos_delta"]
            .mean()
            .sort_index()
        )
        if not grouped.empty:
            laps = grouped.index.to_numpy(dtype=int)
            losses = (-grouped.values).astype(float)
            return laps, losses

    if {"lap_number", "lap_time_sec"}.issubset(df.columns):
        grouped = df.groupby("lap_number", as_index=True)["lap_time_sec"].mean().sort_index()
        laps = grouped.index.to_numpy(dtype=int)
        losses = grouped.values.astype(float)
        return laps, losses

    if {"pit_lap", "final_pos_delta"}.issubset(df.columns):
        grouped = df.groupby("pit_lap", as_index=True)["final_pos_delta"].mean().sort_index()
        laps = grouped.index.to_numpy(dtype=int)
        losses = (-grouped.values).astype(float)
        return laps, losses

    raise ValueError("Could not derive pit optimization inputs from dataset")


@app.post("/abpwo/pit_window")
def pit_window(req: PitWindowRequest):
    import numpy as np

    try:
        season = req.season or 2024
        event = req.event or "Monza"

        if req.laps and req.losses:
            if len(req.laps) != len(req.losses):
                raise ValueError("laps and losses length mismatch")
            laps = np.array(req.laps, dtype=float)
            losses = np.array(req.losses, dtype=float)
            source = "request_payload"
            sample_size = int(len(laps))
        else:
            df, source = load_real_or_synth(season, event)
            df = _subset_by_car(df, req.car_id)
            laps, losses = _abpwo_inputs_from_data(df)
            sample_size = int(len(df))

        car_id_numeric = float(req.car_id) if (req.car_id and str(req.car_id).isdigit()) else 0.0
        result = optimize_pit_lap(
            laps=laps,
            lap_loss=losses,
            car_id=car_id_numeric,
            lap_min=req.lap_min,
            lap_max=req.lap_max,
        )
        return {
            "optimal_lap": int(result.optimal_lap),
            "mean": _safe_float(result.mean),
            "std": _safe_float(result.std),
            "method": result.method,
            "candidate_count": int(len(laps)),
            "sample_size": sample_size,
            "data_source": source,
            "season": season,
            "event": event,
            "car_scope": req.car_id or "RACE",
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc


@app.post("/marl/simulate")
def marl_simulate(req: SimRequest):
    season = req.season or 2024
    event = req.event or "Monza"
    inferred_max_laps = req.max_laps
    source = "default"
    if inferred_max_laps is None:
        df, source = load_real_or_synth(season, event)
        if "lap_number" in df.columns and not df["lap_number"].empty:
            inferred_max_laps = int(df["lap_number"].max())
        else:
            inferred_max_laps = 57
    inferred_max_laps = max(1, int(inferred_max_laps))

    model_path = req.model_path
    if not model_path:
        event_slug = event.lower().replace(" ", "_")
        candidate = f"models/fcsg/{event_slug}_{season}.json"
        model_path = candidate if os.path.exists(candidate) else None

    trace = simulate(model_path, max_laps=inferred_max_laps, checkpoint=req.checkpoint_path)
    final_state = trace[-1] if trace else {}
    ranked = sorted(final_state.items(), key=lambda kv: kv[1].get("position", 99))
    top3 = [car for car, _ in ranked[:3]]
    winner = top3[0] if top3 else None
    avg_tire_age = None
    if final_state:
        avg_tire_age = _safe_float(sum(s.get("tire_age", 0.0) for s in final_state.values()) / len(final_state))
    return {
        "laps": int(len(trace)),
        "planned_laps": inferred_max_laps,
        "winner": winner,
        "top3": top3,
        "avg_tire_age": avg_tire_age,
        "model_path": model_path,
        "season": season,
        "event": event,
        "data_source": source,
    }


@app.post("/csie/query")
def csie_query(req: CFRequest):
    try:
        result = run_counterfactual(req.query, season=req.season or 2023, event=req.event or "Bahrain")
        return result
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "error": str(exc),
                "example_queries": [
                    "If car 16 pits on lap 14 for soft",
                    "If car 1 pits on lap 12 for medium",
                    "Car 16 switches to hard on lap 20",
                    "Safety car appears on lap 22",
                    "Car 44 delay pit by 3 laps from lap 14",
                ],
            },
        ) from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
