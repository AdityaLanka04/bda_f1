"""Run a full simulated race and return lap-by-lap trace."""
from __future__ import annotations

import argparse
import json
import os

from .environment.race_env import RaceEnv
from .agents.ppo_agent import PPOAgent


def simulate(model_path: str | None, max_laps: int = 57, checkpoint: str | None = None):
    env = RaceEnv(model_path=model_path, max_laps=max_laps)
    agent = PPOAgent(checkpoint_path=checkpoint)
    trace = []
    terminated = False
    while not terminated:
        actions = {car: agent.act(state) for car, state in env.state.items()}
        obs, _, terminateds, _, _ = env.step(actions)
        terminated = terminateds.get("__all__", False)
        trace.append(env.state)
    return trace


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="models/fcsg/bahrain_2023.json")
    parser.add_argument("--out", default="data/processed/race_states/simulated_race.json")
    parser.add_argument("--checkpoint", default=None)
    args = parser.parse_args()

    trace = simulate(args.model, checkpoint=args.checkpoint)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(trace, f)
    print(f"Saved simulated race to {args.out}")


if __name__ == "__main__":
    main()
