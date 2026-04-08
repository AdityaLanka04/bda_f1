"""Natural language query parser (expanded patterns)."""
from __future__ import annotations

import re

from .intervention_schema import Intervention

COMPOUNDS = {"soft", "medium", "hard", "inter", "wet"}

# Patterns
PIT_WITH_COMPOUND = re.compile(
    r"(?:car|driver)\s+(?P<car>\w+)\s+(?:pits?|pit|box)\s+(?:on\s+)?lap\s+(?P<lap>\d+)\s+(?:for|to)\s+(?P<compound>soft|medium|hard|inter|wet)",
    re.IGNORECASE,
)

PIT_ON_LAP = re.compile(
    r"(?:car|driver)\s+(?P<car>\w+)\s+(?:pits?|pit|box)\s+(?:on\s+)?lap\s+(?P<lap>\d+)",
    re.IGNORECASE,
)

SWITCH_COMPOUND = re.compile(
    r"(?:car|driver)\s+(?P<car>\w+)\s+(?:switches|switch|changes|change)\s+(?:to\s+)?(?P<compound>soft|medium|hard|inter|wet)\s+(?:on\s+)?lap\s+(?P<lap>\d+)",
    re.IGNORECASE,
)

SAFETY_CAR = re.compile(
    r"(?:safety\s+car|sc)\s+(?:appears|deployed|happens|comes\s+out)\s+(?:on\s+)?lap\s+(?P<lap>\d+)",
    re.IGNORECASE,
)

NO_SAFETY_CAR = re.compile(
    r"(?:no\s+safety\s+car|no\s+sc)\s+(?:on\s+)?lap\s+(?P<lap>\d+)",
    re.IGNORECASE,
)

TRACK_TEMP = re.compile(
    r"(?:track\s+temp|track\s+temperature)\s+(?:is|=)?\s*(?P<temp>\d+(?:\.\d+)?)\s*(?:c|°c)?\s+(?:on\s+)?lap\s+(?P<lap>\d+)",
    re.IGNORECASE,
)

DELAY_PIT = re.compile(
    r"(?:car|driver)\s+(?P<car>\w+)\s+(?:delay|push\s+back|later)\s+(?:pit|pits|pit\s+stop)?\s*by\s+(?P<delta>\d+)\s+laps?(?:\s+(?:from|at)\s+lap\s+(?P<lap>\d+))?",
    re.IGNORECASE,
)

ADVANCE_PIT = re.compile(
    r"(?:car|driver)\s+(?P<car>\w+)\s+(?:advance|earlier|bring\s+forward)\s+(?:pit|pits|pit\s+stop)?\s*by\s+(?P<delta>\d+)\s+laps?(?:\s+(?:from|at)\s+lap\s+(?P<lap>\d+))?",
    re.IGNORECASE,
)

UNDERCUT = re.compile(
    r"(?:car|driver)\s+(?P<car>\w+)\s+undercut\s+(?:on\s+)?lap\s+(?P<lap>\d+)",
    re.IGNORECASE,
)

OVERCUT = re.compile(
    r"(?:car|driver)\s+(?P<car>\w+)\s+overcut\s+(?:on\s+)?lap\s+(?P<lap>\d+)",
    re.IGNORECASE,
)


def _normalize_car(raw: str) -> str:
    return raw.strip().upper()


def parse_query(text: str) -> Intervention:
    t = text.strip()

    m = PIT_WITH_COMPOUND.search(t)
    if m:
        car = _normalize_car(m.group("car"))
        lap = int(m.group("lap"))
        compound = m.group("compound").lower()
        return Intervention(car=car, variable="pit_compound", value=compound, lap=lap)

    m = SWITCH_COMPOUND.search(t)
    if m:
        car = _normalize_car(m.group("car"))
        lap = int(m.group("lap"))
        compound = m.group("compound").lower()
        return Intervention(car=car, variable="pit_compound", value=compound, lap=lap)

    m = PIT_ON_LAP.search(t)
    if m:
        car = _normalize_car(m.group("car"))
        lap = int(m.group("lap"))
        return Intervention(car=car, variable="pit_lap", value=lap, lap=lap)

    m = DELAY_PIT.search(t)
    if m:
        car = _normalize_car(m.group("car"))
        delta = int(m.group("delta"))
        base = m.group("lap")
        if not base:
            raise ValueError("Delay queries must include a base lap, e.g. 'from lap 14'.")
        base_lap = int(base)
        new_lap = base_lap + delta
        return Intervention(car=car, variable="pit_lap", value=new_lap, lap=new_lap)

    m = ADVANCE_PIT.search(t)
    if m:
        car = _normalize_car(m.group("car"))
        delta = int(m.group("delta"))
        base = m.group("lap")
        if not base:
            raise ValueError("Advance queries must include a base lap, e.g. 'from lap 14'.")
        base_lap = int(base)
        new_lap = max(1, base_lap - delta)
        return Intervention(car=car, variable="pit_lap", value=new_lap, lap=new_lap)

    m = SAFETY_CAR.search(t)
    if m:
        lap = int(m.group("lap"))
        return Intervention(car="RACE", variable="safety_car", value=1, lap=lap)

    m = NO_SAFETY_CAR.search(t)
    if m:
        lap = int(m.group("lap"))
        return Intervention(car="RACE", variable="safety_car", value=0, lap=lap)

    m = TRACK_TEMP.search(t)
    if m:
        lap = int(m.group("lap"))
        temp = float(m.group("temp"))
        return Intervention(car="RACE", variable="track_temp", value=temp, lap=lap)

    m = UNDERCUT.search(t)
    if m:
        car = _normalize_car(m.group("car"))
        lap = int(m.group("lap"))
        return Intervention(car=car, variable="strategy_label", value="undercut", lap=lap)

    m = OVERCUT.search(t)
    if m:
        car = _normalize_car(m.group("car"))
        lap = int(m.group("lap"))
        return Intervention(car=car, variable="strategy_label", value="overcut", lap=lap)

    raise ValueError("Could not parse query")
