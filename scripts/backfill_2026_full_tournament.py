"""
backfill_2026_full_tournament.py

One-time backfill: fetches the ENTIRE 2026 World Cup schedule (all 12
groups, all stages, from June 11 to the Final) in a single call, and
syncs it straight into the `matches` table. This fills in matches that
the regular 5-day rolling producer window would have missed (anything
in the past, or far enough in the future).

Run this once now, and optionally re-run it occasionally to catch up
on anything the live pipeline missed.
"""

import os
import requests
import psycopg2
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("FOOTBALL_DATA_TOKEN")
TOURNAMENT_ID = "WC-2026"


def fetch_full_schedule():
    url = "https://api.football-data.org/v4/competitions/WC/matches"
    headers = {"X-Auth-Token": TOKEN}
    params = {"dateFrom": "2026-06-11", "dateTo": "2026-07-19"}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("matches", [])


def get_team_id(cur, team_name):
    if not team_name:
        return None
    cur.execute("SELECT team_id FROM teams WHERE team_name = %s", (team_name,))
    row = cur.fetchone()
    if row:
        return row[0]
    new_id = f"T2026-{abs(hash(team_name)) % 10000}"
    cur.execute(
        "INSERT INTO teams (team_id, team_name) VALUES (%s, %s) ON CONFLICT DO NOTHING",
        (new_id, team_name)
    )
    return new_id


def run():
    conn = psycopg2.connect(
        host=os.getenv("HOST_POSTGRES_HOST", "localhost"),
        port=os.getenv("HOST_POSTGRES_PORT", "5432"),
        dbname=os.getenv("HOST_POSTGRES_DB", "worldcup2026"),
        user=os.getenv("HOST_POSTGRES_USER", "postgres"),
        password=os.getenv("HOST_POSTGRES_PASSWORD"),
    )
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO tournaments (tournament_id, tournament_name, host_country, num_teams)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (tournament_id) DO NOTHING
        """,
        (TOURNAMENT_ID, "2026 FIFA World Cup", "USA/Canada/Mexico", 48)
    )

    matches = fetch_full_schedule()
    print(f"Fetched {len(matches)} total matches from the full tournament schedule")

    synced = 0
    for m in matches:
        home_team = m["homeTeam"]["name"] or "TBD"
        away_team = m["awayTeam"]["name"] or "TBD"
        home_id = get_team_id(cur, home_team)
        away_id = get_team_id(cur, away_team)
        score = m.get("score", {}).get("fullTime", {})

        cur.execute(
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
                f"2026-{m['id']}", TOURNAMENT_ID, m["utcDate"], m.get("stage"), m.get("group"),
                home_id, away_id, score.get("home"), score.get("away"), str(m["id"])
            )
        )
        synced += 1

    cur.close()
    conn.close()
    print(f"Backfill complete. Synced {synced} matches.")


if __name__ == "__main__":
    run()