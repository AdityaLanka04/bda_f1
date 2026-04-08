"""Reward function for race strategy."""
from __future__ import annotations


def compute_reward(start_pos: int, end_pos: int) -> float:
    # Higher reward for positions gained
    return float(start_pos - end_pos)
