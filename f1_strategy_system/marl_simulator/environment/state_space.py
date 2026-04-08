"""State space for each car agent."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CarState:
    lap: int
    tire_age: int
    compound: str
    position: int
    gap_ahead: float
    gap_behind: float
    fuel: float
    drs: bool
