# File: kafka/consumer.py
# This script listens to the "sensor-data" topic and prints messages.

import json
from kafka import KafkaConsumer

# ── CONNECT TO KAFKA ───────────────────────────────────
consumer = KafkaConsumer(
    "sensor-data",                             # topic to listen to
    bootstrap_servers=["localhost:9092"],
    auto_offset_reset="earliest",             # start from the very first message
    enable_auto_commit=True,                  # mark messages as "read" automatically

    # value_deserializer: reverse of producer — bytes → Python dict
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

print("Listening on sensor-data topic...")

# ── LISTEN FOR MESSAGES ────────────────────────────────
for message in consumer:
    # message.value is the dict we sent from the producer
    data = message.value
    print(f"Received: ts={data['timestamp']}, value={data['value']:.2f}")