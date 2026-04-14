# File: backend/preprocessing.py

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import pickle   # for saving the scaler to disk

def load_and_clean(filepath: str) -> pd.DataFrame:
    """Load CSV, parse timestamps, handle missing values."""
    df = pd.read_csv(filepath)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    # Check for missing values
    print(f"Missing values: {df['value'].isna().sum()}")

    # Fill any missing values with the average of neighbors
    # ffill = "forward fill" (copy last known value)
    # bfill = "backward fill" (copy next known value)
    df["value"] = df["value"].ffill().bfill()

    print(f"Loaded {len(df)} rows, {df['value'].isna().sum()} missing after fill")
    return df


def normalize(series: pd.Series, scaler_path: str = "models/scaler.pkl"):
    """
    Scale values to range [0, 1].
    Why? Neural networks train much better with small numbers.
    A value of 78°C becomes 0.47 after scaling.
    """
    scaler = MinMaxScaler(feature_range=(0, 1))

    # fit_transform: learn the min/max, then apply the scaling
    values = series.values.reshape(-1, 1)   # reshape to 2D (scaler expects that)
    scaled = scaler.fit_transform(values).flatten()

    # Save the scaler — we'll need it later to reverse the scaling for display
    with open(scaler_path, "wb") as f:
        pickle.dump(scaler, f)
    print(f"Scaler saved to {scaler_path}")

    return scaled, scaler


def create_sequences(data: np.ndarray, seq_length: int = 50):
    """
    Convert a 1D array into overlapping windows.

    Example with seq_length=3 and data=[1,2,3,4,5]:
      Window 0: [1, 2, 3]
      Window 1: [2, 3, 4]
      Window 2: [3, 4, 5]

    The LSTM learns patterns within each window.
    """
    sequences = []
    for i in range(len(data) - seq_length):
        # Take a slice of length seq_length starting at index i
        window = data[i : i + seq_length]
        sequences.append(window)

    # Convert list of windows to a numpy array
    # Shape: (num_windows, seq_length, 1)
    # The "1" is the number of features (we only have temperature)
    X = np.array(sequences).reshape(-1, seq_length, 1)
    return X


def train_test_split_time(X: np.ndarray, train_ratio: float = 0.8):
    """
    Split sequences into training and test sets.
    IMPORTANT: For time-series, we split by TIME not randomly.
    We train on the past, test on the future.
    """
    split_idx = int(len(X) * train_ratio)
    X_train = X[:split_idx]   # first 80%
    X_test  = X[split_idx:]   # last 20%
    print(f"Train: {X_train.shape}, Test: {X_test.shape}")
    return X_train, X_test


# ── RUN PREPROCESSING ──────────────────────────────────
if __name__ == "__main__":
    # Load
    df = load_and_clean("data/machine_temperature.csv")

    # Normalize
    scaled_values, scaler = normalize(df["value"])

    # Create sequences of length 50 (each input = 50 time steps)
    SEQ_LENGTH = 50
    X = create_sequences(scaled_values, seq_length=SEQ_LENGTH)
    print(f"Total sequences: {X.shape}")   # e.g., (22645, 50, 1)

    # Split
    X_train, X_test = train_test_split_time(X, train_ratio=0.8)

    # Save for use in training script
    np.save("data/X_train.npy", X_train)
    np.save("data/X_test.npy", X_test)
    print("Saved X_train.npy and X_test.npy")