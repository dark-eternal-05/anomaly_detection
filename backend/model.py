# File: backend/model.py
# Full LSTM Autoencoder implementation with explanations.

import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import (
    Input, LSTM, RepeatVector, TimeDistributed, Dense
)
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint


def build_lstm_autoencoder(seq_length: int = 50, n_features: int = 1,
                            encoding_dim: int = 32) -> Model:
    """
    Build the LSTM Autoencoder model.

    Architecture:
    Input (50, 1)
      → LSTM Encoder layer 1 (128 units, returns full sequence)
      → LSTM Encoder layer 2 (encoding_dim units, returns last state only)
      → RepeatVector (repeat the compressed state 50 times)
      → LSTM Decoder layer 1 (encoding_dim units, returns full sequence)
      → LSTM Decoder layer 2 (128 units, returns full sequence)
      → TimeDistributed Dense (1 output per timestep)
    Output (50, 1)
    """

    # ── ENCODER ──────────────────────────────────────────
    # Input: sequences of shape (50 time steps, 1 feature)
    inputs = Input(shape=(seq_length, n_features), name="encoder_input")

    # First LSTM layer: 128 memory units
    # return_sequences=True means output at EVERY timestep (not just last)
    # This lets the next LSTM layer see the full sequence
    x = LSTM(128, activation="tanh",
             return_sequences=True, name="encoder_lstm1")(inputs)

    # Second LSTM layer: compresses to encoding_dim values
    # return_sequences=False = only return the LAST output (the summary)
    encoded = LSTM(encoding_dim, activation="tanh",
                   return_sequences=False, name="encoder_lstm2")(x)

    # ── BOTTLENECK ───────────────────────────────────────
    # At this point, "encoded" has shape (batch_size, encoding_dim)
    # It's the compressed representation

    # RepeatVector: repeat the encoded vector seq_length times
    # Gives shape (batch_size, 50, encoding_dim)
    # Why? The decoder LSTM needs a sequence as input, not a single vector
    repeated = RepeatVector(seq_length, name="bottleneck")(encoded)

    # ── DECODER ──────────────────────────────────────────
    # Mirror image of encoder
    x = LSTM(encoding_dim, activation="tanh",
             return_sequences=True, name="decoder_lstm1")(repeated)

    x = LSTM(128, activation="tanh",
             return_sequences=True, name="decoder_lstm2")(x)

    # TimeDistributed Dense: apply the same Dense layer to EACH timestep
    # output: 1 value per timestep → reconstructs the original sequence
    outputs = TimeDistributed(Dense(n_features), name="decoder_output")(x)

    # ── BUILD MODEL ───────────────────────────────────────
    model = Model(inputs=inputs, outputs=outputs, name="LSTM_Autoencoder")

    # Compile: define how the model learns
    # optimizer="adam" = efficient gradient descent algorithm
    # loss="mse" = Mean Squared Error (how different is output vs input?)
    model.compile(optimizer="adam", loss="mse")

    print(model.summary())
    return model


def train_model(model: Model, X_train: np.ndarray,
                epochs: int = 50, batch_size: int = 32,
                save_path: str = "models/lstm_ae.h5") -> dict:
    """
    Train the autoencoder.
    Input == Target: we're teaching it to reconstruct its own input.
    """

    # EarlyStopping: stop training if validation loss stops improving
    # patience=5 = stop if no improvement for 5 epochs
    # restore_best_weights = revert to the best model seen during training
    early_stop = EarlyStopping(
        monitor="val_loss",
        patience=5,
        restore_best_weights=True
    )

    # ModelCheckpoint: save the best model to disk during training
    checkpoint = ModelCheckpoint(
        save_path,
        save_best_only=True,
        monitor="val_loss",
        verbose=1
    )

    # model.fit() runs the training
    # X_train is BOTH input AND target (autoencoder: learn to reconstruct input)
    history = model.fit(
        X_train, X_train,           # input = target
        epochs=epochs,
        batch_size=batch_size,
        validation_split=0.1,       # use 10% of training data for validation
        callbacks=[early_stop, checkpoint],
        verbose=1
    )

    print(f"\nTraining complete. Best val_loss: {min(history.history['val_loss']):.6f}")
    return history.history


def get_reconstruction_errors(model: Model, X: np.ndarray) -> np.ndarray:
    """
    Run model on sequences, return reconstruction error for each.
    Higher error = more anomalous.
    """
    X_pred = model.predict(X, verbose=0)   # shape: (N, 50, 1)

    # Mean Squared Error per sequence
    # np.mean(..., axis=(1,2)) averages over timesteps and features
    errors = np.mean(np.power(X - X_pred, 2), axis=(1, 2))
    return errors   # shape: (N,)


def load_saved_model(path: str) -> Model:
    """Load a previously trained model from disk."""
    model = load_model(path)
    print(f"Model loaded from {path}")
    return model
