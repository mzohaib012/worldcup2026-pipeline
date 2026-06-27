"""
load_historical_data.py

Airflow DAG — Phase 1: one-time (manually triggered) backfill of historical
World Cup data into PostgreSQL.
"""

from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

import sys
sys.path.append("/opt/airflow/scripts/data_loader")

from load_kaggle_historical import run_full_load


default_args = {
    "owner": "zohaib",
    "retries": 1,
}

with DAG(
    dag_id="load_historical_world_cup_data",
    default_args=default_args,
    description="One-time backfill of 1930-2022 World Cup data into PostgreSQL",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["worldcup", "phase1", "historical"],
) as dag:

    full_load_task = PythonOperator(
        task_id="run_full_historical_load",
        python_callable=run_full_load,
    )