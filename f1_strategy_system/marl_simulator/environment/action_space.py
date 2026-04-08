"""Action space definitions."""
ACTIONS = ["stay_out", "pit_soft", "pit_medium", "pit_hard", "pit_inter", "pit_wet"]
ACTION_TO_ID = {a: i for i, a in enumerate(ACTIONS)}
ID_TO_ACTION = {i: a for a, i in ACTION_TO_ID.items()}
ACTION_TO_COMPOUND = {
    "pit_soft": "soft",
    "pit_medium": "medium",
    "pit_hard": "hard",
    "pit_inter": "inter",
    "pit_wet": "wet",
}
