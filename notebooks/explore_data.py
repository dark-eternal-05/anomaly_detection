# File: notebooks/explore_data.py
# Run with: python notebooks/explore_data.py

import pandas as pd
import matplotlib.pyplot as plt

# ── LOAD DATA ──────────────────────────────────────────
# read_csv turns the CSV file into a Python "DataFrame" (like a table)
df = pd.read_csv("data/machine_temperature.csv")

# Convert the "timestamp" column from plain text to actual datetime objects
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Sort by time (important — data must be in order)
df = df.sort_values("timestamp").reset_index(drop=True)

# ── INSPECT DATA ───────────────────────────────────────
print("Shape:", df.shape)           # (number of rows, number of columns)
print("Columns:", df.columns.tolist())
print("\nFirst 5 rows:")
print(df.head())
print("\nBasic statistics:")
print(df["value"].describe())       # min, max, mean, etc.

# ── PLOT ───────────────────────────────────────────────
plt.figure(figsize=(15, 5))         # width=15 inches, height=5 inches

plt.plot(df["timestamp"], df["value"],
         color="steelblue",
         linewidth=0.8,
         label="Temperature")

# Mark the known anomaly region (machine failure happened ~Dec 19-20)
# We'll highlight a window around that period
anomaly_start = pd.Timestamp("2013-12-19")
anomaly_end   = pd.Timestamp("2013-12-21")
plt.axvspan(anomaly_start, anomaly_end,
            color="red", alpha=0.2, label="Known anomaly")

plt.title("Machine Temperature Over Time")
plt.xlabel("Time")
plt.ylabel("Temperature (°C)")
plt.legend()
plt.tight_layout()
plt.savefig("data/temperature_plot.png", dpi=150)
plt.show()
print("Plot saved to data/temperature_plot.png")