# Setup Guide (Summary)

A full UI setup guide is in `f1_setup_guide.jsx`. This is the CLI summary.

1. Create venv and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Copy env file:

```bash
cp .env.example .env
```

3. Start Docker services:

```bash
docker compose up -d
```

4. Verify:

```bash
python -c "import fastf1, pyspark, torch; print('OK')"
```

5. Run streaming pipeline:

```bash
python -m ingestion.openf1_stream
python -m pipeline.streaming_job
```
