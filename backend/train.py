# File: backend/train.py
# Run this script to train the model.

import numpy as np
import matplotlib.pyplot as plt
from model import build_lstm_autoencoder, train_model

# ── LOAD PREPROCESSED DATA ─────────────────────────────
X_train = np.load("data/X_train.npy")
X_test  = np.load("data/X_test.npy")
print(f"Training on {X_train.shape[0]} sequences")

# ── BUILD AND TRAIN ────────────────────────────────────
model = build_lstm_autoencoder(seq_length=50, encoding_dim=32)
history = train_model(model, X_train, epochs=50, batch_size=32,
                      save_path="models/lstm_ae.h5")

# ── PLOT TRAINING LOSS ─────────────────────────────────
plt.figure(figsize=(10, 4))
plt.plot(history["loss"],     label="Training Loss",   color="steelblue")
plt.plot(history["val_loss"], label="Validation Loss", color="orange", linestyle="--")
plt.xlabel("Epoch")
plt.ylabel("MSE Loss")
plt.title("LSTM Autoencoder Training Progress")
plt.legend()
plt.tight_layout()
plt.savefig("models/training_loss.png", dpi=150)
plt.show()
print("Training complete! Model saved to models/lstm_ae.h5")
