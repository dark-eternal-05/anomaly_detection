# File: backend/anomaly.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from model import load_saved_model, get_reconstruction_errors


def detect_anomalies(errors: np.ndarray,
                     threshold_percentile: float = 95) -> np.ndarray:
    """
    Flag sequences as anomalies if their reconstruction error is
    above the Nth percentile of ALL errors.

    Why percentile instead of a fixed number?
    Because errors vary per dataset. The 95th percentile always flags
    the top 5% most unusual sequences regardless of scale.
    """
    threshold = np.percentile(errors, threshold_percentile)
    print(f"Threshold (p{threshold_percentile}): {threshold:.6f}")

    anomaly_flags = errors > threshold
    print(f"Anomalies detected: {anomaly_flags.sum()} / {len(errors)} sequences")
    return anomaly_flags


def plot_anomalies(errors: np.ndarray, anomaly_flags: np.ndarray,
                   threshold: float):
    """Plot reconstruction errors with anomaly threshold and highlighted points."""
    plt.figure(figsize=(15, 5))

    # Plot reconstruction error for every sequence
    plt.plot(errors, color="steelblue", linewidth=0.7,
             label="Reconstruction error", alpha=0.8)

    # Mark anomalous points in red
    anomaly_indices = np.where(anomaly_flags)[0]
    plt.scatter(anomaly_indices, errors[anomaly_indices],
                color="red", s=20, zorder=5, label="Anomaly")

    # Draw threshold line
    plt.axhline(y=threshold, color="orange", linestyle="--", linewidth=1.5,
                label=f"Threshold = {threshold:.4f}")

    plt.xlabel("Sequence index")
    plt.ylabel("Reconstruction MSE")
    plt.title("Anomaly Detection Results")
    plt.legend()
    plt.tight_layout()
    plt.savefig("models/anomaly_detection_results.png", dpi=150)
    plt.show()


# ── RUN DETECTION ──────────────────────────────────────
if __name__ == "__main__":
    X_test = np.load("data/X_test.npy")
    model  = load_saved_model("models/lstm_ae.h5")

    errors = get_reconstruction_errors(model, X_test)
    threshold = np.percentile(errors, 95)
    anomaly_flags = detect_anomalies(errors, threshold_percentile=95)

    plot_anomalies(errors, anomaly_flags, threshold)

    # Save results for the API to serve
    results = pd.DataFrame({
        "sequence_index": np.arange(len(errors)),
        "reconstruction_error": errors,
        "is_anomaly": anomaly_flags,
        "threshold": threshold
    })
    results.to_csv("data/anomaly_results.csv", index=False)
    print("Results saved to data/anomaly_results.csv")