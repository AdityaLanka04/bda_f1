"""Schema for causal interventions."""
from __future__ import annotations

from pydantic import BaseModel


class Intervention(BaseModel):
    car: str
    variable: str
    value: str | int | float
    lap: int
