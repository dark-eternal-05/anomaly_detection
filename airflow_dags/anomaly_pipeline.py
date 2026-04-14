# File: airflow_dags/anomaly_pipeline.py
# This defines the 4-step pipeline that Airflow will run automatically.

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# ── DEFINE EACH TASK AS A PYTHON FUNCTION ─────────────

def task_ingest_data():
    """Step 1: Download/refresh the dataset."""
    import subprocess
    print("Ingesting latest data...")
    # In production you'd pull from a real data source (API, database, etc.)
    # Here we just confirm the file exists
    import os
    if os.path.exists("/opt/airflow/data/machine_temperature.csv"):
        print("Data file found. Rows:", sum(1 for _ in open(
            "/opt/airflow/data/machine_temperature.csv")))
    else:
        raise FileNotFoundError("Dataset not found!")


def task_preprocess():
    """Step 2: Run preprocessing — normalize, create sequences."""
    import sys
    sys.path.insert(0, "/opt/airflow")
    from backend.preprocessing import load_and_clean, normalize, create_sequences, train_test_split_time
    import numpy as np

    df = load_and_clean("/opt/airflow/data/machine_temperature.csv")
    scaled, scaler = normalize(df["value"], "/opt/airflow/models/scaler.pkl")
    X = create_sequences(scaled, seq_length=50)
    X_train, X_test = train_test_split_time(X)
    np.save("/opt/airflow/data/X_train.npy", X_train)
    np.save("/opt/airflow/data/X_test.npy", X_test)
    print("Preprocessing done")


def task_train_model():
    """Step 3: Train (or retrain) the LSTM Autoencoder."""
    import numpy as np
    from backend.model import build_lstm_autoencoder, train_model

    X_train = np.load("/opt/airflow/data/X_train.npy")
    model = build_lstm_autoencoder(seq_length=50)
    train_model(model, X_train, epochs=20,
                save_path="/opt/airflow/models/lstm_ae.h5")
    print("Model trained and saved")


def task_run_predictions():
    """Step 4: Run model on test data, flag anomalies, save results."""
    import numpy as np
    import pandas as pd
    from backend.model import load_saved_model, get_reconstruction_errors
    from backend.anomaly import detect_anomalies

    X_test = np.load("/opt/airflow/data/X_test.npy")
    model = load_saved_model("/opt/airflow/models/lstm_ae.h5")
    errors = get_reconstruction_errors(model, X_test)
    anomaly_flags = detect_anomalies(errors, threshold_percentile=95)

    results = pd.DataFrame({
        "reconstruction_error": errors,
        "is_anomaly": anomaly_flags
    })
    results.to_csv("/opt/airflow/data/anomaly_results.csv", index=False)
    print(f"Predictions done. Anomalies found: {anomaly_flags.sum()}")


# ── DEFINE THE DAG ─────────────────────────────────────
# default_args: applied to every task unless overridden
default_args = {
    "owner": "anomaly_team",
    "retries": 1,                            # retry once if a task fails
    "retry_delay": timedelta(minutes=5),     # wait 5 min before retrying
}

with DAG(
    dag_id="anomaly_detection_pipeline",
    default_args=default_args,
    description="End-to-end anomaly detection pipeline",
    schedule_interval="@daily",              # run every day
    start_date=datetime(2024, 1, 1),
    catchup=False,                           # don't run for past dates
    tags=["anomaly", "lstm", "mlops"],
) as dag:

    # Create task objects
    ingest     = PythonOperator(task_id="ingest_data",      python_callable=task_ingest_data)
    preprocess = PythonOperator(task_id="preprocess_data",  python_callable=task_preprocess)
    train      = PythonOperator(task_id="train_model",      python_callable=task_train_model)
    predict    = PythonOperator(task_id="run_predictions",  python_callable=task_run_predictions)

    # Define order: ingest → preprocess → train → predict
    # The >> operator means "then run"
    ingest >> preprocess >> train >> predict