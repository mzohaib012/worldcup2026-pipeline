"""
test_consumer.py

Simple consumer to verify messages landed in the Kafka topic.
Reads from the beginning and prints each message, then exits.
"""

import json
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    "raw_match_events",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    enable_auto_commit=False,
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    consumer_timeout_ms=5000  # stop after 5 seconds of no new messages
)

print("Reading messages from 'raw_match_events'...\n")
count = 0
for message in consumer:
    count += 1
    event = message.value
    print(f"[{count}] {event['home_team']} vs {event['away_team']} | {event['status']} | {event['home_score']}-{event['away_score']}")

print(f"\nTotal messages read: {count}")