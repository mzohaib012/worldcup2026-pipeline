"""
live_match_pipeline.py

Phase 2 DAG — fetches live 2026 World Cup matches and pushes them
through Kafka into TimescaleDB. Runs every 10 minutes.
"""

from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

import sys
sys.path.append("/opt/airflow/scripts/kafka_producer")
sys.path.append("/opt/airflow/scripts")

from live_match_producer import fetch_today_matches, push_to_kafka
from timescale_consumer import run_consumer
from sync_live_to_matches import sync

default_args = {
    "owner": "zohaib",
    "retries": 1,
}

with DAG(
    dag_id="live_world_cup_2026_pipeline",
    default_args=default_args,
    description="Fetch live 2026 World Cup matches -> Kafka -> TimescaleDB",
    schedule="*/10 * * * *",   # every 10 minutes
    start_date=datetime(2026, 6, 1),
    catchup=False,
    tags=["worldcup", "phase2", "live"],
) as dag:

    def _produce():
        matches = fetch_today_matches()
        print(f"Found {len(matches)} matches today")
        push_to_kafka(matches)

    def _consume():
        run_consumer()

    def _sync():
        sync()

    produce_task = PythonOperator(task_id="produce_to_kafka", python_callable=_produce)
    consume_task = PythonOperator(task_id="consume_to_timescale", python_callable=_consume)
    sync_task = PythonOperator(task_id="sync_to_matches_table", python_callable=_sync)

    produce_task >> consume_task >> sync_task