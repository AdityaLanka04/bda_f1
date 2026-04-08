# Distributed F1 Strategy System (FCSG + ABPWO + MARL-RS + CSIE)

This repository is a **full-stack prototype** for a distributed F1 race strategy platform:

- **FCSG**: Federated Causal Strategy Graph learned from distributed telemetry.
- **ABPWO**: Adaptive Bayesian Pit Window Optimizer with real-time updates.
- **MARL-RS**: Multi-agent race simulator driven by the learned causal model.
- **CSIE**: Natural-language counterfactual strategy explorer.

The implementation is designed to be **runnable end-to-end** with realistic interfaces, while keeping the heavy ML pieces lightweight and swappable.

## Quick Start (Local)

1. Create virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Copy environment template:

```bash
cp .env.example .env
```

3. Start infra (Kafka + MLflow):

```bash
docker compose up -d
```

4. Run a minimal demo pipeline:

```bash
python -m fcsg.train_fcsg --circuit bahrain --season 2023
python -m abpwo.evaluate_abpwo --circuit bahrain --season 2023
python -m marl_simulator.simulate_race --circuit bahrain --season 2023
python -m csie.counterfactual_engine --query "If car 16 pits on lap 14 for soft, what happens?"
```

5. Start API:

```bash
python serving/fastapi_app.py
```

Then open `http://127.0.0.1:8000/docs`.

## Streaming Pipeline (Kafka + Flink-style)

1. Start the OpenF1 stream producer (synthetic by default):

```bash
python -m ingestion.openf1_stream
```

2. Run the streaming job (Kafka consumer + Flink-style processing + persistence):

```bash
python -m pipeline.streaming_job
```

This writes:
- `data/processed/race_states/streamed.parquet`
- `models/abpwo/posteriors/*.json`

## Structure

See `docs/architecture.md` and `f1_project_structure.jsx` for the full tree.

## Notes

- This is a **prototype implementation**, not a production race strategy engine.
- All modules are built so you can swap in real models (DoWhy, BoTorch, RLlib, etc.) later.
