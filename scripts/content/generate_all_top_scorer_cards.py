"""
generate_all_top_scorer_cards.py

Batch-generates player cards for the top N all-time World Cup scorers,
reusing the same generate_card() function used for single-player testing.
"""

import os
import time
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

from generate_player_card import generate_card

load_dotenv()


def get_engine():
    host = os.getenv("HOST_POSTGRES_HOST", "localhost")
    port = os.getenv("HOST_POSTGRES_PORT", "5432")
    db = os.getenv("HOST_POSTGRES_DB", "worldcup2026")
    user = os.getenv("HOST_POSTGRES_USER", "postgres")
    password = os.getenv("HOST_POSTGRES_PASSWORD", "")
    return create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}")


def get_top_scorers(engine, limit=20):
    query = """
        SELECT p.full_name, COUNT(*) AS goals
        FROM players p
        JOIN match_goals g ON p.player_id = g.player_id
        GROUP BY p.full_name
        ORDER BY goals DESC
        LIMIT %(limit)s
    """
    return pd.read_sql(query, engine, params={"limit": limit})


def run(limit=20):
    engine = get_engine()
    top_scorers = get_top_scorers(engine, limit)
    print(f"Generating cards for top {len(top_scorers)} scorers...\n")

    for _, row in top_scorers.iterrows():
        name = row["full_name"]
        print(f"-> {name} ({row['goals']} goals)")
        try:
            generate_card(name)
        except Exception as e:
            print(f"   Failed for {name}: {e}")
        time.sleep(0.3)  # be polite to Wikipedia's API

    print("\nBatch generation complete.")


if __name__ == "__main__":
    run(limit=20)