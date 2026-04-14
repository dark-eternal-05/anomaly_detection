# File: backend/api.py
# FastAPI server — run with: uvicorn backend.api:app --reload --port 8000

import asyncio
import json
import numpy as np
import pandas as pd
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from kafka import KafkaConsumer

import sys, os
sys.path.insert(0, os.path.dirname(__file__))  # add backend/ to path

from model import load_saved_model, get_reconstruction_errors
from anomaly import detect_anomalies

# ── CREATE FASTAPI APP ─────────────────────────────────
app = FastAPI(title="Anomaly Detection API", version="1.0.0")

# CORS: allow the React frontend (running on port 3000) to call this API
# Without this, the browser blocks cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── LOAD MODEL AT STARTUP ──────────────────────────────
# These variables are loaded once when the server starts
model = None
anomaly_results = None

@app.on_event("startup")
async def startup_event():
    global model, anomaly_results
    try:
        model = load_saved_model("models/lstm_ae.h5")
        anomaly_results = pd.read_csv("data/anomaly_results.csv")
        print("Model and results loaded successfully")
    except Exception as e:
        print(f"Warning: Could not load model — {e}")


# ── ENDPOINT 1: GET ALL ANOMALIES ──────────────────────
@app.get("/anomalies")
def get_anomalies(limit: int = 1000):
    """
    Returns stored anomaly detection results.
    React dashboard calls this on load.
    """
    if anomaly_results is None:
        return {"error": "Results not loaded yet"}

    # Filter to anomaly rows only
    anomalies = anomaly_results[anomaly_results["is_anomaly"] == True]

    return {
        "total_sequences": len(anomaly_results),
        "total_anomalies": int(anomalies.shape[0]),
        "threshold": float(anomaly_results["threshold"].iloc[0]),
        "data": anomaly_results.head(limit).to_dict(orient="records")
    }


# ── ENDPOINT 2: PREDICT ON SINGLE SEQUENCE ────────────
@app.post("/predict")
async def predict(payload: dict):
    """
    Accepts a sequence of 50 values, returns reconstruction error and anomaly flag.

    Example request body:
    { "sequence": [57.6, 57.2, 56.9, ..., 58.1] }
    """
    if model is None:
        return {"error": "Model not loaded"}

    sequence = payload.get("sequence", [])
    if len(sequence) != 50:
        return {"error": f"Expected 50 values, got {len(sequence)}"}

    # Reshape to (1, 50, 1) — batch of 1 sequence
    X = np.array(sequence).reshape(1, 50, 1).astype("float32")

    # Run model
    X_pred = model.predict(X, verbose=0)
    error = float(np.mean(np.power(X - X_pred, 2)))

    # Compare to stored threshold
    threshold = float(anomaly_results["threshold"].iloc[0]) if anomaly_results is not None else 0.01
    is_anomaly = error > threshold

    return {
        "reconstruction_error": round(error, 6),
        "threshold": round(threshold, 6),
        "is_anomaly": is_anomaly
    }


# ── ENDPOINT 3: WEBSOCKET for live stream ─────────────
# WebSocket = persistent two-way connection
# Instead of React asking "any new data?" every second,
# the server pushes new data the moment it arrives.
connected_clients = []

@app.websocket("/stream")
async def websocket_stream(websocket: WebSocket):
    """
    Opens a WebSocket. Sends one data point every second from Kafka.
    React connects to ws://localhost:8000/stream and receives live data.
    """
    await websocket.accept()
    connected_clients.append(websocket)
    print(f"WebSocket client connected. Total: {len(connected_clients)}")

    try:
        # Connect to Kafka consumer
        consumer = KafkaConsumer(
            "sensor-data",
            bootstrap_servers=["localhost:9092"],
            auto_offset_reset="latest",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            consumer_timeout_ms=1000   # don't block forever
        )

        while True:
            for kafka_message in consumer:
                data = kafka_message.value
                await websocket.send_json({
                    "timestamp": data["timestamp"],
                    "value": data["value"],
                    "type": "sensor_data"
                })
                await asyncio.sleep(0.05)   # throttle to 20 messages/sec

    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        print("Client disconnected")


# ── HEALTH CHECK ───────────────────────────────────────
@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "results_loaded": anomaly_results is not None
    }