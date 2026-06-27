"""
sync_live_to_matches.py

Bridges live TimescaleDB match_events into the batch `matches` table,
so dbt models (group_standings, round_of_32_qualifiers, etc.) automatically
pick up 2026 World Cup results as they happen.

Idempotent: uses ON CONFLICT to upsert by api_match_id, so re-running
this safely overwrites with the latest score/status instead of duplicating.
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

TIMESCALE_HOST = os.getenv("TIMESCALE_HOST", "localhost")
TIMESCALE_PORT = os.getenv("TIMESCALE_PORT", "5433")
HOST_POSTGRES_HOST = os.getenv("HOST_POSTGRES_HOST", "localhost")
HOST_POSTGRES_PORT = os.getenv("HOST_POSTGRES_PORT", "5432")
HOST_POSTGRES_DB = os.getenv("HOST_POSTGRES_DB", "worldcup2026")
HOST_POSTGRES_USER = os.getenv("HOST_POSTGRES_USER", "postgres")
HOST_POSTGRES_PASSWORD = os.getenv("HOST_POSTGRES_PASSWORD")

TOURNAMENT_ID = "WC-2026"


def ensure_tournament_exists(pg_cur):
    pg_cur.execute(
        """
        INSERT INTO tournaments (tournament_id, tournament_name, host_country, num_teams)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (tournament_id) DO NOTHING
        """,
        (TOURNAMENT_ID, "2026 FIFA World Cup", "USA/Canada/Mexico", 48)
    )


def get_team_id(pg_cur, team_name):
    pg_cur.execute("SELECT team_id FROM teams WHERE team_name = %s", (team_name,))
    row = pg_cur.fetchone()
    if row:
        return row[0]
    # team not in historical data (e.g. new debutant) — create it
    new_id = f"T2026-{abs(hash(team_name)) % 10000}"
    pg_cur.execute(
        "INSERT INTO teams (team_id, team_name) VALUES (%s, %s) ON CONFLICT DO NOTHING",
        (new_id, team_name)
    )
    return new_id


def sync():
    ts_conn = psycopg2.connect(
        host=TIMESCALE_HOST, port=TIMESCALE_PORT,
        dbname="matchevents", user="tsuser", password="tspass"
    )
    ts_cur = ts_conn.cursor()

    pg_conn = psycopg2.connect(
        host=HOST_POSTGRES_HOST, port=HOST_POSTGRES_PORT,
        dbname=HOST_POSTGRES_DB, user=HOST_POSTGRES_USER, password=HOST_POSTGRES_PASSWORD
    )
    pg_conn.autocommit = True
    pg_cur = pg_conn.cursor()

    ensure_tournament_exists(pg_cur)

    # Latest snapshot per match_id (dedupes the at-least-once duplicates)
    ts_cur.execute(
        """
        SELECT DISTINCT ON (match_id)
            match_id, home_team, away_team, status, home_score, away_score,
            stage, group_name, utc_date
        FROM match_events
        ORDER BY match_id, time DESC
        """
    )
    rows = ts_cur.fetchall()
    print(f"Syncing {len(rows)} unique matches...")

    for row in rows:
        match_id, home_team, away_team, status, home_score, away_score, stage, group_name, utc_date = row
        home_team_id = get_team_id(pg_cur, home_team)
        away_team_id = get_team_id(pg_cur, away_team)

        pg_cur.execute(
            """
            INSERT INTO matches (match_id, tournament_id, match_date, stage, group_name,
                                  home_team_id, away_team_id, home_score, away_score, api_match_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (match_id) DO UPDATE SET
                home_score = EXCLUDED.home_score,
                away_score = EXCLUDED.away_score,
                stage = EXCLUDED.stage,
                group_name = EXCLUDED.group_name
            """,
            (
                f"2026-{match_id}", TOURNAMENT_ID, utc_date, stage, group_name,
                home_team_id, away_team_id, home_score, away_score, str(match_id)
            )
        )
        print(f"Synced: {home_team} vs {away_team} | {status}")

    ts_cur.close(); ts_conn.close()
    pg_cur.close(); pg_conn.close()
    print("Sync complete.")


if __name__ == "__main__":
    sync()