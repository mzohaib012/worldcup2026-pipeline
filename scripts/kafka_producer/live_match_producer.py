"""
live_match_producer.py

Fetches today's 2026 World Cup matches from football-data.org
and pushes each match as a JSON message to the Kafka topic 'raw_match_events'.
"""

import os
import json
from datetime import datetime, timezone, timedelta
import requests
from kafka import KafkaProducer
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("FOOTBALL_DATA_TOKEN")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC = "raw_match_events"


def get_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )


def fetch_today_matches():
    """
    Fetches a 5-day forward window (not just today), so the pipeline also
    captures upcoming fixtures -- needed for the countdown timer and the
    schedule view, not just whatever's happening right now.
    """
    url = "https://api.football-data.org/v4/competitions/WC/matches"
    headers = {"X-Auth-Token": TOKEN}
    today = datetime.now(timezone.utc)
    date_from = today.strftime("%Y-%m-%d")
    date_to = (today + timedelta(days=5)).strftime("%Y-%m-%d")
    params = {"dateFrom": date_from, "dateTo": date_to}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("matches", [])


def push_to_kafka(matches):
    producer = get_producer()
    for match in matches:
        # Knockout fixtures are sometimes published before both teams are
        # determined ("Winner of Group A vs Winner of Group B"). The API
        # returns null for those -- label as TBD instead of literal "None"
        # so the bracket UI can show a placeholder shield.
        home_team = match["homeTeam"]["name"] or "TBD"
        away_team = match["awayTeam"]["name"] or "TBD"

        event = {
            "match_id": match["id"],
            "home_team": home_team,
            "away_team": away_team,
            "status": match["status"],
            "minute": match.get("minute"),
            "home_score": match["score"]["fullTime"]["home"],
            "away_score": match["score"]["fullTime"]["away"],
            "stage": match.get("stage"),
            "group_name": match.get("group"),
            "utc_date": match["utcDate"],
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
        
        producer.send(TOPIC, value=event)
        print(f"Pushed: {event['home_team']} vs {event['away_team']} | {event['status']}")
    producer.flush()
    producer.close()


if __name__ == "__main__":
    matches = fetch_today_matches()
    print(f"Found {len(matches)} matches today")
    push_to_kafka(matches)