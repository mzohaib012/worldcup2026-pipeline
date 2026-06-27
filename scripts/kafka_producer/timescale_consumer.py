"""
timescale_consumer.py

Consumes match events from Kafka and writes them into TimescaleDB.
Stops automatically after 10 seconds of no new messages (good for
both manual runs and scheduled Airflow runs).
"""

import os
import json
from datetime import datetime, timezone
from kafka import KafkaConsumer
import psycopg2
from dotenv import load_dotenv

load_dotenv()

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TIMESCALE_HOST = os.getenv("TIMESCALE_HOST", "localhost")
TIMESCALE_PORT = os.getenv("TIMESCALE_PORT", "5433")


def run_consumer():
    consumer = KafkaConsumer(
        "raw_match_events",
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="timescale-writer",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        consumer_timeout_ms=10000
    )

    conn = psycopg2.connect(
        host=TIMESCALE_HOST,
        port=TIMESCALE_PORT,
        dbname="matchevents",
        user="tsuser",
        password="tspass"
    )
    conn.autocommit = True
    cur = conn.cursor()

    print("Listening for match events...\n")
    count = 0
    for message in consumer:
        event = message.value
        cur.execute(
            """
            INSERT INTO match_events (time, match_id, home_team, away_team, status, minute, home_score, away_score)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                datetime.now(timezone.utc),
                event["match_id"],
                event["home_team"],
                event["away_team"],
                event["status"],
                event.get("minute"),
                event["home_score"],
                event["away_score"],
            )
        )
        count += 1
        print(f"Inserted: {event['home_team']} vs {event['away_team']} | {event['status']}")

    cur.close()
    conn.close()
    print(f"\nTotal inserted: {count}")


if __name__ == "__main__":
    run_consumer()