"""RLlib training entrypoint (production-style).

If RLlib isn't installed, it will fall back to the lightweight curriculum trainer.
"""
from __future__ import annotations

import argparse
import os

from .agents.curriculum_trainer import train_curriculum
from .environment.race_env import RaceEnv


def train_rllib(num_cars: int, iterations: int, checkpoint_dir: str) -> None:
    try:
        from ray.tune.registry import register_env
        from ray.rllib.algorithms.ppo import PPOConfig
        from ray.rllib.env.multi_agent_env import MultiAgentEnv
    except Exception:
        train_curriculum(stages=(num_cars,))
        return

    class MultiCarEnv(MultiAgentEnv):
        def __init__(self, config):
            self.env = RaceEnv(num_cars=config.get("num_cars", num_cars))

        def reset(self, *, seed=None, options=None):
            obs, info = self.env.reset(seed=seed, options=options)
            return obs, info

        def step(self, action_dict):
            return self.env.step(action_dict)

    register_env("multi_car_env", lambda cfg: MultiCarEnv(cfg))

    config = (
        PPOConfig()
        .environment("multi_car_env", env_config={"num_cars": num_cars})
        .framework("torch")
        .rollouts(num_rollout_workers=0)
        .training(train_batch_size=400)
    )
    algo = config.build()

    os.makedirs(checkpoint_dir, exist_ok=True)
    for i in range(iterations):
        result = algo.train()
        if (i + 1) % 5 == 0:
            algo.save(checkpoint_dir)
            print(f"Checkpoint saved at iter {i+1}")
        print("iter", i + 1, "reward", result.get("episode_reward_mean"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_cars", type=int, default=20)
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--out", default="models/marl")
    args = parser.parse_args()

    train_rllib(args.num_cars, args.iterations, args.out)


if __name__ == "__main__":
    main()
