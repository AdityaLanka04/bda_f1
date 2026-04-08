"""Airflow DAG placeholder for race day streaming."""
from datetime import datetime

try:
    from airflow import DAG
    from airflow.operators.bash import BashOperator
except Exception:
    DAG = None

if DAG:
    with DAG(
        "race_day",
        schedule_interval=None,
        start_date=datetime(2023, 1, 1),
        catchup=False,
    ) as dag:
        BashOperator(
            task_id="openf1_stream",
            bash_command="python -m ingestion.openf1_stream",
        )
