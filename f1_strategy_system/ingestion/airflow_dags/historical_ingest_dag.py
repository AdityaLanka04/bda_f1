"""Airflow DAG placeholder for historical ingestion."""
from datetime import datetime

try:
    from airflow import DAG
    from airflow.operators.bash import BashOperator
except Exception:  # Airflow optional
    DAG = None

if DAG:
    with DAG(
        "historical_ingest",
        schedule_interval=None,
        start_date=datetime(2023, 1, 1),
        catchup=False,
    ) as dag:
        BashOperator(
            task_id="fastf1_loader",
            bash_command="python -m ingestion.fastf1_loader --season 2023 --event Bahrain --session R",
        )
