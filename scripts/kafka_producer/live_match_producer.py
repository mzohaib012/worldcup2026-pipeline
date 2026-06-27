"""
live_match_producer.py

Fetches today's 2026 World Cup matches from football-data.org
and pushes each match as a JSON message to the Kafka topic 'raw_match_events'.
"""

import os
import json
from datetime import datetime, timezone
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
    url = "https://api.football-data.org/v4/competitions/WC/matches"
    headers = {"X-Auth-Token": TOKEN}
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    params = {"dateFrom": today, "dateTo": today}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("matches", [])


def push_to_kafka(matches):
    producer = get_producer()
    for match in matches:
        event = {
            "match_id": match["id"],
            "home_team": match["homeTeam"]["name"],
            "away_team": match["awayTeam"]["name"],
            "status": match["status"],
            "minute": match.get("minute"),
            "home_score": match["score"]["fullTime"]["home"],
            "away_score": match["score"]["fullTime"]["away"],
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