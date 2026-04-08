from marl_simulator.environment.race_env import RaceEnv


def test_race_env_step():
    env = RaceEnv(num_cars=3, max_laps=2)
    obs, _ = env.reset()
    actions = {car: "stay_out" for car in obs.keys()}
    next_obs, _, terminateds, _, _ = env.step(actions)
    assert len(next_obs) == 3
    assert terminateds["__all__"] is False
