"""
load_kaggle_historical.py

Loads historical World Cup match + goal data into PostgreSQL.
Source: matches.csv + goals.csv (Fjelstul World Cup Database export).
Both raw files use inconsistent header styles — column names are normalized
to snake_case right after reading, so everything below uses one consistent
naming convention regardless of how the original CSV was formatted.
"""

import pandas as pd
from pathlib import Path
from db_connection import get_engine

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"


def _normalize_columns(df):
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df


def load_matches_source():
    df = pd.read_csv(DATA_DIR / "matches.csv", encoding="cp1252")
    return _normalize_columns(df)


def load_goals_source():
    df = pd.read_csv(DATA_DIR / "goals.csv", encoding="cp1252")
    return _normalize_columns(df)


def build_tournaments(matches_df, engine):
    rows = []
    for (tid, tname), group in matches_df.groupby(["tournament_id", "tournament_name"]):
        host_modes = group["country_name"].mode()
        host_country = host_modes.iat[0] if not host_modes.empty else None
        num_teams = pd.concat([group["home_team_id"], group["away_team_id"]]).nunique()
        rows.append({
            "tournament_id": tid,
            "tournament_name": tname,
            "host_country": host_country,
            "num_teams": num_teams,
        })
    out = pd.DataFrame(rows)
    out.to_sql("tournaments", engine, if_exists="append", index=False, method="multi", chunksize=500)
    print(f"Loaded {len(out)} tournaments")


def build_teams(matches_df, goals_df, engine):
    home = matches_df[["home_team_id", "home_team_name", "home_team_code"]].rename(
        columns={"home_team_id": "team_id", "home_team_name": "team_name", "home_team_code": "team_code"})
    away = matches_df[["away_team_id", "away_team_name", "away_team_code"]].rename(
        columns={"away_team_id": "team_id", "away_team_name": "team_name", "away_team_code": "team_code"})
    g_team = goals_df[["team_id", "team_name", "team_code"]]
    g_player_team = goals_df[["player_team_id", "player_team_name", "player_team_code"]].rename(
        columns={"player_team_id": "team_id", "player_team_name": "team_name", "player_team_code": "team_code"})

    teams = pd.concat([home, away, g_team, g_player_team]).dropna(subset=["team_id"])
    teams = teams.drop_duplicates(subset="team_id")
    teams["confederation"] = None
    teams.to_sql("teams", engine, if_exists="append", index=False, method="multi", chunksize=500)
    print(f"Loaded {len(teams)} teams")


def build_matches(matches_df, engine):
    out = matches_df.copy()
    out["match_date"] = pd.to_datetime(out["match_date"], errors="coerce").dt.date

    out = out.rename(columns={
        "stage_name": "stage",
        "home_team_score": "home_score",
        "away_team_score": "away_score",
        "stadium_name": "venue",
        "city_name": "city",
        "country_name": "country",
    })
    cols = ["match_id", "tournament_id", "match_date", "stage", "group_name",
            "home_team_id", "away_team_id", "home_score", "away_score",
            "venue", "city", "country", "result"]
    out = out[cols]
    out.to_sql("matches", engine, if_exists="append", index=False, method="multi", chunksize=500)
    print(f"Loaded {len(out)} matches")


def build_players(goals_df, engine):
    players = goals_df[["player_id", "given_name", "family_name", "player_team_id"]].drop_duplicates(subset="player_id")
    # Some mononym players (Ronaldo, Pelé) have the literal text "Not Applicable"
    # instead of a real given name in the source data — treat that as blank.
    players["given_name"] = players["given_name"].replace(
        to_replace=r"(?i)^not applicable$", value="", regex=True
    )
    players["full_name"] = (players["given_name"].fillna("") + " " + players["family_name"].fillna("")).str.strip()


def build_match_goals(goals_df, engine):
    out = goals_df.rename(columns={
        "minute_regulation": "minute",
        "penalty": "is_penalty",
        "own_goal": "is_own_goal",
    })
    cols = ["goal_id", "match_id", "player_id", "team_id", "minute",
            "minute_stoppage", "is_penalty", "is_own_goal"]
    out = out[cols]
    out["is_penalty"] = out["is_penalty"].fillna(0).astype(int).astype(bool)
    out["is_own_goal"] = out["is_own_goal"].fillna(0).astype(int).astype(bool)
    out.to_sql("match_goals", engine, if_exists="append", index=False, method="multi", chunksize=500)
    print(f"Loaded {len(out)} goals")


def run_full_load():
    engine = get_engine()
    matches_df = load_matches_source()
    goals_df = load_goals_source()

    build_tournaments(matches_df, engine)
    build_teams(matches_df, goals_df, engine)
    build_matches(matches_df, engine)
    build_players(goals_df, engine)
    build_match_goals(goals_df, engine)
    print("Historical load complete.")


if __name__ == "__main__":
    run_full_load()