"""PPO agent wrapper with optional RLlib policy loading."""
from __future__ import annotations

import random
from ..environment.action_space import ACTIONS
from ..environment.race_env import RaceEnv


class PPOAgent:
    def __init__(self, checkpoint_path: str | None = None):
        self.algo = None
        if checkpoint_path:
            try:
                from ray.rllib.algorithms.ppo import PPO
                self.algo = PPO.from_checkpoint(checkpoint_path)
            except Exception:
                self.algo = None

    def act(self, state: dict) -> str:
        if self.algo is not None:
            # Convert state to observation vector using RaceEnv helper
            env = RaceEnv(num_cars=1)
            obs = env._obs(state)
            action_id = self.algo.compute_single_action(obs)
            if isinstance(action_id, (list, tuple)):
                action_id = action_id[0]
            return ACTIONS[int(action_id)]
        return random.choice(ACTIONS)
