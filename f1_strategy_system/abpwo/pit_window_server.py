"""FastAPI app serving pit window recommendations."""
from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from .bayesian_optimizer import optimize_pit_lap

app = FastAPI(title="ABPWO Pit Window Service")


class PitWindowRequest(BaseModel):
    laps: list[int]
    losses: list[float]
    car_id: int | None = None
    lap_min: int | None = None
    lap_max: int | None = None


@app.post("/pit_window")
def pit_window(req: PitWindowRequest):
    import numpy as np
    result = optimize_pit_lap(
        laps=np.array(req.laps),
        lap_loss=np.array(req.losses),
        car_id=req.car_id,
        lap_min=req.lap_min,
        lap_max=req.lap_max,
    )
    return {
        "optimal_lap": int(result.optimal_lap),
        "mean": result.mean,
        "std": result.std,
        "method": result.method,
    }


if __name__ == "__main__":
    import numpy as np
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8100)
