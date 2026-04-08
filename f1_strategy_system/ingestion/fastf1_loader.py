"""
FastF1 loader for historical sessions.

This is a pragmatic implementation that can run in two modes:
- If FastF1 is installed and online, it fetches real data.
- Otherwise it produces a small synthetic dataset for development.
"""
from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from typing import Optional

import pandas as pd


@dataclass
class SessionRequest:
    season: int
    event: str
    session: str


def _synthetic_laps() -> pd.DataFrame:
    data = []
    for lap in range(1, 6):
        data.append({
            "driver": "VER",
            "lap": lap,
            "lap_time": 90.0 + lap * 0.4,
            "compound": "soft" if lap < 3 else "medium",
            "pit": 1 if lap == 3 else 0,
        })
    return pd.DataFrame(data)


def load_session(req: SessionRequest, cache_dir: Optional[str] = None) -> pd.DataFrame:
    try:
        import fastf1
    except Exception:
        return _synthetic_laps()

    if cache_dir:
        fastf1.Cache.enable_cache(cache_dir)

    session = fastf1.get_session(req.season, req.event, req.session)
    session.load(laps=True, telemetry=False, weather=False)
    laps = session.laps

    # Select a compact set of columns to keep sizes reasonable.
    cols = ["Driver", "LapNumber", "LapTime", "Compound", "PitInTime"]
    out = laps[cols].copy()
    out.columns = ["driver", "lap", "lap_time", "compound", "pit_in_time"]
    out["pit"] = out["pit_in_time"].notna().astype(int)
    out["lap_time"] = out["lap_time"].dt.total_seconds()
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", type=int, default=2023)
    parser.add_argument("--event", type=str, default="Bahrain")
    parser.add_argument("--session", type=str, default="R")
    parser.add_argument("--out", type=str, default="data/processed/lap_features/laps.parquet")
    parser.add_argument("--cache", type=str, default=os.getenv("FASTF1_CACHE_DIR", "data/raw/fastf1_cache"))
    args = parser.parse_args()

    req = SessionRequest(args.season, args.event, args.session)
    df = load_session(req, args.cache)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    df.to_parquet(args.out, index=False)
    print(f"Saved {len(df)} laps to {args.out}")


if __name__ == "__main__":
    main()
