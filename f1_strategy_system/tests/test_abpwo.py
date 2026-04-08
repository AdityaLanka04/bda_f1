import numpy as np
from abpwo.bayesian_optimizer import optimize_pit_lap


def test_optimize_pit_lap():
    laps = np.arange(10, 30)
    losses = (laps - 20) ** 2
    result = optimize_pit_lap(laps, losses)
    assert 10 <= result.optimal_lap <= 30
