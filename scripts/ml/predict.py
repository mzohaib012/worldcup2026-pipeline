"""
predict.py

Loads the trained model and predicts win probability between two teams
by name. Used standalone here; will be wired into FastAPI in Phase 5.
"""

import os
from pathlib import Path
import pandas as pd
import joblib
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

MODELS_DIR = Path(__file__).resolve().parents[2] / "data" / "models"

FEATURE_COLS = [
    "home_avg_goals_for", "home_avg_goals_against", "home_matches_played",
    "away_avg_goals_for", "away_avg_goals_against", "away_matches_played",
]


def get_engine():
    host = os.getenv("HOST_POSTGRES_HOST", "localhost")
    port = os.getenv("HOST_POSTGRES_PORT", "5432")
    db = os.getenv("HOST_POSTGRES_DB", "worldcup2026")
    user = os.getenv("HOST_POSTGRES_USER", "postgres")
    password = os.getenv("HOST_POSTGRES_PASSWORD", "")
    return create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}")


def predict_match(home_team_name, away_team_name):
    model = joblib.load(MODELS_DIR / "win_probability_model.joblib")
    team_stats = pd.read_csv(MODELS_DIR / "team_stats.csv")

    engine = get_engine()
    teams = pd.read_sql("SELECT team_id, team_name FROM teams", engine)

    home_id = teams.loc[teams["team_name"] == home_team_name, "team_id"].values
    away_id = teams.loc[teams["team_name"] == away_team_name, "team_id"].values

    if len(home_id) == 0 or len(away_id) == 0:
        print("One or both team names not found in database.")
        return

    home_stats = team_stats[team_stats["team_id"] == home_id[0]]
    away_stats = team_stats[team_stats["team_id"] == away_id[0]]

    if home_stats.empty or away_stats.empty:
        print("No historical stats available for one of the teams.")
        return

    features = pd.DataFrame([{
        "home_avg_goals_for": home_stats["avg_goals_for"].values[0],
        "home_avg_goals_against": home_stats["avg_goals_against"].values[0],
        "home_matches_played": home_stats["matches_played"].values[0],
        "away_avg_goals_for": away_stats["avg_goals_for"].values[0],
        "away_avg_goals_against": away_stats["avg_goals_against"].values[0],
        "away_matches_played": away_stats["matches_played"].values[0],
    }])

    probs = model.predict_proba(features[FEATURE_COLS])[0]
    classes = model.classes_

    print(f"\n{home_team_name} vs {away_team_name}")
    for cls, prob in zip(classes, probs):
        print(f"  {cls}: {prob:.1%}")


if __name__ == "__main__":
    predict_match("Brazil", "Argentina")