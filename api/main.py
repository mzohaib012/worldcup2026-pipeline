"""
main.py

FastAPI serving layer for the World Cup 2026 pipeline. Exposes the dbt
analytics models, ML predictions, the Catch-Me-Up live digest, and
auto-generated player card images.
"""

import os
import sys
from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import create_engine
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(str(Path(__file__).resolve().parents[1] / "scripts" / "ml"))
sys.path.append(str(Path(__file__).resolve().parents[1] / "scripts" / "content"))

from predict import predict_match
from generate_player_card import generate_card

load_dotenv()

app = FastAPI(
    title="World Cup 2026 Pipeline API",
    description="Standings, top scorers, head-to-head, win predictions, and player cards.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
PLAYER_CARDS_DIR = Path(__file__).resolve().parents[1] / "data" / "player_cards"


def get_engine():
    host = os.getenv("HOST_POSTGRES_HOST", "localhost")
    port = os.getenv("HOST_POSTGRES_PORT", "5432")
    db = os.getenv("HOST_POSTGRES_DB", "worldcup2026")
    user = os.getenv("HOST_POSTGRES_USER", "postgres")
    password = os.getenv("HOST_POSTGRES_PASSWORD", "")
    return create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}")


@app.get("/")
def root():
    return {
        "message": "World Cup 2026 Pipeline API",
        "endpoints": [
            "/standings/{tournament_id}",
            "/top-scorers",
            "/head-to-head/{team_a}/{team_b}",
            "/predict/{home_team}/{away_team}",
            "/player-card/{player_name}",
            "/catch-me-up",
        ],
    }


@app.get("/standings/{tournament_id}")
def get_standings(tournament_id: str, group: Optional[str] = None):
    engine = get_engine()
    query = "SELECT * FROM group_standings WHERE tournament_id = %(tid)s"
    params = {"tid": tournament_id}
    if group:
        query += " AND group_name = %(group)s"
        params["group"] = group
    df = pd.read_sql(query, engine, params=params)
    if df.empty:
        raise HTTPException(status_code=404, detail="No standings found for this tournament/group")
    return df.to_dict(orient="records")


@app.get("/top-scorers")
def get_top_scorers(limit: int = 10):
    engine = get_engine()
    df = pd.read_sql(f"SELECT * FROM top_scorers LIMIT {limit}", engine)
    return df.to_dict(orient="records")


@app.get("/head-to-head/{team_a}/{team_b}")
def get_head_to_head(team_a: str, team_b: str):
    engine = get_engine()
    query = """
        SELECT * FROM head_to_head
        WHERE (team_a_name ILIKE %(a)s AND team_b_name ILIKE %(b)s)
           OR (team_a_name ILIKE %(b)s AND team_b_name ILIKE %(a)s)
    """
    df = pd.read_sql(query, engine, params={"a": team_a, "b": team_b})
    if df.empty:
        raise HTTPException(status_code=404, detail="No head-to-head record found for these teams")
    return df.to_dict(orient="records")[0]


@app.get("/predict/{home_team}/{away_team}")
def get_prediction(home_team: str, away_team: str):
    import io
    import contextlib

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        predict_match(home_team, away_team)
    output = buf.getvalue()

    if "not found" in output or "No historical stats" in output:
        raise HTTPException(status_code=404, detail=output.strip())

    probs = {}
    for line in output.strip().split("\n")[1:]:
        if ":" in line:
            label, value = line.strip().split(":")
            probs[label.strip()] = value.strip()
    return {"home_team": home_team, "away_team": away_team, "probabilities": probs}


@app.get("/player-card/{player_name}")
def get_player_card(player_name: str):
    safe_name = player_name.replace(" ", "_")
    card_path = PLAYER_CARDS_DIR / f"{safe_name}_card.png"

    if not card_path.exists():
        generated = generate_card(player_name)
        if generated is None:
            raise HTTPException(status_code=404, detail=f"No data found for player '{player_name}'")
        card_path = generated

    return FileResponse(card_path, media_type="image/png")


@app.get("/catch-me-up")
def catch_me_up():
    engine = get_engine()
    query = """
        SELECT home_team, away_team, status, home_score, away_score, time
        FROM match_events
        WHERE time > NOW() - INTERVAL '24 hours'
        ORDER BY time DESC
        LIMIT 10
    """
    df = pd.read_sql(query, create_engine(
        f"postgresql+psycopg2://tsuser:tspass@{os.getenv('TIMESCALE_HOST_LOCAL', 'localhost')}:5433/matchevents"
    ))
    summaries = []
    for _, row in df.iterrows():
        home_score = int(row["home_score"]) if pd.notna(row["home_score"]) else None
        away_score = int(row["away_score"]) if pd.notna(row["away_score"]) else None

        if row["status"] == "FINISHED":
            summaries.append(f"{row['home_team']} {home_score}-{away_score} {row['away_team']} (FT)")
        elif row["status"] in ("IN_PLAY", "LIVE"):
            summaries.append(f"{row['home_team']} {home_score}-{away_score} {row['away_team']} (LIVE)")
        else:
            summaries.append(f"{row['home_team']} vs {row['away_team']} - upcoming")
    return {"catch_me_up": summaries}