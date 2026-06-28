"""
train_model.py

Builds a simple win-probability model from historical World Cup matches.

CAVEAT (worth knowing for interviews): this uses each team's career-average
stats across ALL tournaments — not "stats as of that specific match date".
That's a simplified version of what's called data leakage avoidance — a real
production model would use only stats available *before* each match. Doing
it this way keeps the project achievable while still being a genuine,
explainable ML model. Mentioning this trade-off explicitly is itself a good
signal in interviews.
"""

import os
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
from dotenv import load_dotenv

load_dotenv()

MODELS_DIR = Path(__file__).resolve().parents[2] / "data" / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

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


def build_team_stats(engine):
    query = """
        SELECT home_team_id AS team_id, home_score AS goals_for, away_score AS goals_against
        FROM matches WHERE home_score IS NOT NULL
        UNION ALL
        SELECT away_team_id AS team_id, away_score AS goals_for, home_score AS goals_against
        FROM matches WHERE away_score IS NOT NULL
    """
    df = pd.read_sql(query, engine)
    return df.groupby("team_id").agg(
        avg_goals_for=("goals_for", "mean"),
        avg_goals_against=("goals_against", "mean"),
        matches_played=("goals_for", "count"),
    ).reset_index()


def build_training_data(engine, team_stats):
    matches = pd.read_sql(
        "SELECT * FROM matches WHERE home_score IS NOT NULL AND away_score IS NOT NULL", engine
    )

    df = matches.merge(team_stats, left_on="home_team_id", right_on="team_id", how="left")
    df = df.rename(columns={
        "avg_goals_for": "home_avg_goals_for",
        "avg_goals_against": "home_avg_goals_against",
        "matches_played": "home_matches_played",
    }).drop(columns=["team_id"])

    df = df.merge(team_stats, left_on="away_team_id", right_on="team_id", how="left")
    df = df.rename(columns={
        "avg_goals_for": "away_avg_goals_for",
        "avg_goals_against": "away_avg_goals_against",
        "matches_played": "away_matches_played",
    }).drop(columns=["team_id"])

    df = df.dropna(subset=["home_avg_goals_for", "away_avg_goals_for"])

    def get_result(row):
        if row["home_score"] > row["away_score"]:
            return "HOME_WIN"
        if row["home_score"] < row["away_score"]:
            return "AWAY_WIN"
        return "DRAW"

    df["result"] = df.apply(get_result, axis=1)
    return df[FEATURE_COLS + ["result"]]


def train():
    engine = get_engine()

    print("Building team stats...")
    team_stats = build_team_stats(engine)
    print(f"Stats built for {len(team_stats)} teams")

    print("Building training dataset...")
    training_df = build_training_data(engine, team_stats)
    print(f"Training rows: {len(training_df)}")

    X = training_df[FEATURE_COLS]
    y = training_df["result"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    print(f"\nTest accuracy: {accuracy_score(y_test, preds):.2%}")
    print("\nClassification report:")
    print(classification_report(y_test, preds))

    joblib.dump(model, MODELS_DIR / "win_probability_model.joblib")
    team_stats.to_csv(MODELS_DIR / "team_stats.csv", index=False)
    print(f"\nModel saved to {MODELS_DIR / 'win_probability_model.joblib'}")


if __name__ == "__main__":
    train()