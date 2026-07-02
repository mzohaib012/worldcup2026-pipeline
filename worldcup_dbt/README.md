# 🏆 World Cup 2026 Data Engineering Platform

> End-to-end data pipeline covering historical World Cup data (1930–2022) and the live FIFA 2026 tournament — streaming, ML predictions, auto-generated player cards, and a React dashboard.

[![CI](https://github.com/mzohaib012/worldcup2026-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/mzohaib012/worldcup2026-pipeline/actions)

---

## Architecture
football-data.org API
↓
Python Poller (5-day rolling window)
↓
Apache Kafka (raw_match_events topic)
↓
Python Consumer → TimescaleDB (match_events hypertable)
↓
Sync Bridge → PostgreSQL (matches table)
↓
dbt Models (standings, top scorers, H2H, knockout bracket, Round of 32 qualifier)
↓
FastAPI (REST endpoints)
↓
React + Tailwind Dashboard

---

## Features

| Feature | Description |
|---|---|
| 🔴 Live Scoreboard | Live match score or countdown to next kickoff |
| ⚡ Catch Me Up | Auto-scrolling ticker of today's results |
| 📊 Group Standings | All 12 groups, real-time from dbt |
| 🏟️ Knockout Bracket | Round of 32 to Final with SVG connecting lines |
| ⚽ Top Scorers | All-time leaders with auto-generated FIFA-style player cards |
| 🤖 Win Predictor | Random Forest ML model (58% accuracy on historical data) |
| 📅 Schedule | Upcoming fixtures and results with tabs |
| ⚔️ Head-to-Head | Player comparison with radar chart |
| 🎉 Animations | Goal confetti burst and full-screen winner celebration |

---

## Tech Stack

**Ingestion:** Python, Apache Kafka (KRaft), Apache Airflow

**Storage:** PostgreSQL (historical), TimescaleDB (live events)

**Transformation:** dbt (6 models)

**ML:** scikit-learn RandomForestClassifier

**Content Generation:** Pillow, matplotlib (FIFA-style player cards)

**API:** FastAPI + uvicorn

**Frontend:** React + Vite + Tailwind CSS v4 + Recharts

**Infrastructure:** Docker Compose

**CI/CD:** GitHub Actions

---

## Two-Laptop Setup

| Machine | Runs |
|---|---|
| HP Laptop | VS Code, PostgreSQL (native), FastAPI, React |
| Toshiba Laptop | Docker Desktop (Kafka, TimescaleDB, Airflow) |

Both on the same LAN. Docker containers connect to PostgreSQL via host.docker.internal.

---

## Quick Start

Prerequisites: Python 3.11+, Node 20+, Docker Desktop, PostgreSQL

**Step 1 — Clone**
```bash
git clone https://github.com/mzohaib012/worldcup2026-pipeline.git
cd worldcup2026-pipeline
```

**Step 2 — Environment**
```bash
cp .env.example .env
# Fill in your PostgreSQL credentials and football-data.org API token
```

**Step 3 — Start Docker services**
```bash
docker-compose up -d
```

**Step 4 — Install Python dependencies**
```bash
pip install -r requirements.txt
```

**Step 5 — Database setup**

In pgAdmin: create database `worldcup2026`, then run `sql/schema.sql`.

```bash
python scripts/data_loader/load_kaggle_historical.py
python scripts/backfill_2026_full_tournament.py
```

**Step 6 — dbt models**
```bash
cd worldcup_dbt && dbt run && cd ..
```

**Step 7 — Start API**
```bash
python -m uvicorn api.main:app --reload
```

**Step 8 — Start dashboard**
```bash
cd frontend && npm install && npm run dev
```

Open `http://localhost:5173`

---

## Project Structure
worldcup2026-pipeline/
├── api/                         FastAPI serving layer
├── airflow/dags/                Airflow DAGs
├── data/
│   ├── models/                  Trained ML model
│   ├── player_cards/            Auto-generated player card PNGs
│   └── raw/                     Kaggle CSVs (gitignored)
├── frontend/                    React + Tailwind dashboard
├── scripts/
│   ├── content/                 Player card generator
│   ├── data_loader/             Historical data loader
│   ├── kafka_producer/          Live match producer and consumer
│   ├── ml/                      ML training and prediction
│   └── sync_live_to_matches.py  Live-to-batch bridge
├── sql/schema.sql               PostgreSQL schema
├── worldcup_dbt/                dbt project (6 models)
└── docker-compose.yml           Kafka + TimescaleDB + Airflow

---

## ML Model

**Algorithm:** Random Forest Classifier

**Features:** Team average goals for/against, matches played (home + away)

**Training data:** 970 historical World Cup matches (1930-2022)

**Test accuracy:** 58.25%

**Note:** Uses career-average stats. Full time-travel feature engineering would require match-by-match rolling stats — acknowledged simplification, good interview discussion point.

---

## Data Sources

- **Historical data:** Kaggle World Cup datasets (1930-2022)
- **Live data:** football-data.org free tier API
- **Player photos:** Wikipedia/Wikimedia Commons (freely licensed)

---

*Built by [Zohaib](https://github.com/mzohaib012) — Data Engineer*

*Live data powered by [football-data.org](https://www.football-data.org)*