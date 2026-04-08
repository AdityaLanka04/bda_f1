"""Curriculum trainer placeholder."""
from __future__ import annotations

from .ppo_agent import PPOAgent
from ..environment.race_env import RaceEnv


def train_curriculum(stages=(2, 5, 10, 20)) -> None:
    for n in stages:
        env = RaceEnv(num_cars=n)
        agent = PPOAgent()
        env.reset()
        terminated = False
        while not terminated:
            actions = {car: agent.act(state) for car, state in env.state.items()}
            _, _, terminateds, _, _ = env.step(actions)
            terminated = terminateds.get("__all__", False)
        print(f"Stage {n} completed")
