# System Architecture

This document describes the end-to-end architecture of the Distributed F1 Strategy System.

## Data Flow

1. **Ingestion**: FastF1/Jolpica/OpenF1 provide telemetry and results.
2. **Streaming**: Kafka ingests live events; Flink-style processor updates race state in near real-time.
3. **Preprocessing**: Spark + Flink generate lap and stint features.
4. **FCSG**: Federated causal discovery learns a circuit-specific DAG.
5. **ABPWO**: Bayesian optimizer computes optimal pit windows per car.
6. **MARL-RS**: Multi-agent simulator rolls out race scenarios using FCSG transitions.
7. **CSIE**: Analysts ask natural language counterfactuals that run do-calculus + MARL replay.

## Key Interfaces

- `fcsg/causal_inference/dowhy_estimator.py` exposes ATE estimation.
- `abpwo/pit_window_server.py` serves pit recommendations.
- `marl_simulator/simulate_race.py` returns lap-by-lap race traces.
- `csie/csie_api.py` exposes counterfactual scenarios.
