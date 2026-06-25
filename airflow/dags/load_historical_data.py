from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

import sys
sys.path.append("/opt/airflow/scripts/data_loader")

from load_kaggle_historical import load_tournaments, load_teams, load_players, load_matches
from db_connection import get_engine

default_args = {"owner": "zohaib", "retries": 1}

with DAG(
    dag_id="load_historical_world_cup_data",
    default_args=default_args,
    description="One-time backfill of 1930-2022 World Cup data into PostgreSQL",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["worldcup", "phase1", "historical"],
) as dag:

    def _load_tournaments():
        load_tournaments(get_engine())

    def _load_teams():
        load_teams(get_engine())

    def _load_players():
        load_players(get_engine())

    def _load_matches():
        load_matches(get_engine())

    t1 = PythonOperator(task_id="load_tournaments", python_callable=_load_tournaments)
    t2 = PythonOperator(task_id="load_teams", python_callable=_load_teams)
    t3 = PythonOperator(task_id="load_players", python_callable=_load_players)
    t4 = PythonOperator(task_id="load_matches", python_callable=_load_matches)

    t1 >> t2 >> t3 >> t4