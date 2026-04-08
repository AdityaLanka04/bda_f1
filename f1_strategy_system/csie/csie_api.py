"""FastAPI CSIE service."""
from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from .counterfactual_engine import run_counterfactual
from .uncertainty_quantifier import quantify

app = FastAPI(title="CSIE")


class Query(BaseModel):
    query: str
    season: int | None = 2023
    event: str | None = "Bahrain"


@app.post("/csie/query")
def query(req: Query):
    result = run_counterfactual(req.query, season=req.season or 2023, event=req.event or "Bahrain")
    uq = quantify(result["intervention"], runs=50)
    return {"result": result, "uncertainty": uq}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8200)
