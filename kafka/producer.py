# File: kafka/producer.py
# This script reads rows from our CSV and sends them to Kafka one by one,
# simulating a real-time sensor stream.

import json
import time
import pandas as pd
from kafka import KafkaProducer

# ── CONNECT TO KAFKA ───────────────────────────────────
producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],   # address of our Kafka broker

    # value_serializer: how to convert Python dict → bytes for Kafka
    # json.dumps turns dict to string, .encode turns string to bytes
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

print("Connected to Kafka producer")

# ── LOAD DATA ──────────────────────────────────────────
df = pd.read_csv("data/machine_temperature.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])

# ── STREAM ROWS ────────────────────────────────────────
for idx, row in df.iterrows():
    message = {
        "timestamp": str(row["timestamp"]),   # convert datetime to string
        "value": float(row["value"]),          # ensure it's a Python float
        "row_id": idx                           # track position
    }

    # send() puts the message on the "sensor-data" topic
    producer.send("sensor-data", value=message)

    # Print every 100 rows so we can see progress
    if idx % 100 == 0:
        print(f"Sent row {idx}: {message}")

    # Sleep 0.01 seconds between messages = ~100 messages/second
    # In real life, this would be actual sensor timing
    time.sleep(0.01)

# flush() makes sure all messages are actually sent before script exits
producer.flush()
print("Done sending all data!")