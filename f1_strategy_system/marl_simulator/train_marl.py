"""Train MARL agents (attempt RLlib, fallback to curriculum)."""
from __future__ import annotations

from .rllib_train import train_rllib


def main() -> None:
    train_rllib(num_cars=20, iterations=5, checkpoint_dir="models/marl")


if __name__ == "__main__":
    main()
