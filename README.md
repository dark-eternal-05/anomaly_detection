# Real-Time Anomaly Detection System

> **LSTM Autoencoder · Apache Kafka · Apache Spark · Apache Airflow · React Dashboard**

An end-to-end ML system that streams industrial sensor data, detects anomalies using a deep learning model, and visualises results on a live React dashboard — all running on a single Windows 11 machine.

---

## What It Does

Industrial machines, networks, and financial systems behave abnormally before they fail. Manually watching thousands of sensor readings is impossible. This system does it automatically:

1. **Streams** raw sensor readings through Kafka in real time
2. **Processes** the stream with Spark (cleaning, filtering, batching)
3. **Detects** anomalies using an LSTM Autoencoder trained on normal patterns
4. **Schedules** the full pipeline (ingest → preprocess → train → predict) with Airflow
5. **Displays** live results on a React dashboard with auto-updating charts

---

## Architecture

```
Dataset (NAB CSV)
      │
      ▼
Kafka Producer  ──►  Kafka Topic: sensor-data
                            │
                            ▼
                      Apache Spark
                    (stream processor)
                            │
                            ▼
                   LSTM Autoencoder
                  (anomaly detection)
                            │
                            ▼
                      FastAPI Backend
                    /predict  /anomalies
                      /stream (WebSocket)
                            │
                            ▼
                    React Dashboard
               (live chart + anomaly alerts)

           ┌─────────────────────────────┐
           │  Apache Airflow (scheduler) │
           │  ingest → preprocess →      │
           │  train → predict  @daily    │
           └─────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Streaming | Apache Kafka 3.6 | Real-time message queue |
| Processing | Apache Spark 3.5 + PySpark | Parallel stream processing |
| ML Model | TensorFlow 2.15 (LSTM Autoencoder) | Unsupervised anomaly detection |
| Orchestration | Apache Airflow 2.10 | Pipeline scheduling & monitoring |
| Backend API | FastAPI + WebSockets | REST API + live data push |
| Frontend | React + Chart.js | Live dashboard |
| Dataset | NAB (Numenta Anomaly Benchmark) | Real industrial sensor data |
| Platform | Windows 11 + WSL2 (Ubuntu) | Development environment |

---

## Project Structure

```
anomaly_detection/
│
├── backend/
│   ├── api.py                # FastAPI server (REST + WebSocket)
│   ├── model.py              # LSTM Autoencoder architecture + training
│   ├── anomaly.py            # Threshold detection logic
│   ├── preprocessing.py      # Data cleaning, normalisation, sequences
│   └── train.py              # Training entry point
│
├── kafka/
│   ├── producer.py           # Streams CSV rows to Kafka topic
│   └── consumer.py           # Test consumer (development only)
│
├── spark/
│   └── stream_processor.py   # PySpark Kafka stream processing
│
├── airflow_dags/
│   └── anomaly_pipeline.py   # 4-step Airflow DAG (scheduled daily)
│
├── frontend/dashboard/
│   └── src/
│       ├── App.jsx            # Root dashboard component
│       ├── api.js             # Backend HTTP calls
│       ├── hooks/
│       │   └── useWebSocket.js  # Live data WebSocket hook
│       └── components/
│           ├── LiveChart.jsx    # Chart.js line graph with anomaly markers
│           └── StatusCard.jsx   # Summary metric cards
│
├── data/                     # Downloaded datasets + processed arrays (git-ignored)
├── models/                   # Saved model weights + scaler (git-ignored)
├── notebooks/                # Data exploration scripts
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Dataset

**NAB — Machine Temperature System Failure**
- Source: [Numenta Anomaly Benchmark](https://github.com/numenta/NAB)
- 22,695 rows of industrial machine temperature readings (5-minute intervals)
- Contains a known machine failure event (Dec 19–20, 2013)
- No labels needed — the model learns normal patterns unsupervised

```powershell
# Download
Invoke-WebRequest `
  -Uri "https://raw.githubusercontent.com/numenta/NAB/master/data/realKnownCause/machine_temperature_system_failure.csv" `
  -OutFile "data/machine_temperature.csv"
```

---

## How the Model Works

The LSTM Autoencoder is trained **only on normal data**. It learns to compress and reconstruct normal patterns.

```
Input sequence (50 timesteps)
        │
   LSTM Encoder          ← learns normal patterns
        │
   Bottleneck (32 values) ← compressed representation
        │
   LSTM Decoder          ← reconstructs the input
        │
Output sequence (50 timesteps)

Reconstruction Error = mean((input - output)²)

Normal data  → low error   (model has seen this pattern)
Anomaly data → high error  (model cannot reconstruct it)

Threshold = 95th percentile of training errors
```

---

## Prerequisites

| Tool | Version | Notes |
|---|---|---|
| Python | 3.11 | `winget install Python.Python.3.11` |
| Node.js | 20 LTS | `winget install OpenJS.NodeJS.LTS` |
| Java (OpenJDK) | 17 | `winget install Microsoft.OpenJDK.17` |
| Apache Spark | 3.5.0 | Extract to `C:\tools\spark` |
| Apache Kafka | 3.6.0 | Extract to `C:\tools\kafka` |
| WSL2 + Ubuntu | — | `wsl --install` (for Airflow) |
| winutils.exe | hadoop-3.3.6 | Required for Spark on Windows |

---

## Installation

### 1 — Clone and create virtual environment

```powershell
git clone <your-repo-url>
cd anomaly_detection

python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2 — Set required environment variables

Add these to your PowerShell session (or System environment variables):

```powershell
$env:SPARK_HOME            = "C:\tools\spark"
$env:JAVA_HOME             = "C:\PROGRA~1\MICROS~1\JDK-17~1.8-H"   # short path, no spaces
$env:HADOOP_HOME           = "C:\tools\hadoop"
$env:PYSPARK_PYTHON        = "C:\anomaly_detection\venv\Scripts\python.exe"
$env:PYSPARK_DRIVER_PYTHON = "C:\anomaly_detection\venv\Scripts\python.exe"
$env:PATH                  = "C:\tools\spark\bin;$env:JAVA_HOME\bin;C:\tools\hadoop\bin;" + $env:PATH
```

> **Windows note:** `JAVA_HOME` must use the 8.3 short path (no spaces) to avoid a PySpark `WinError 2`. Run `(New-Object -ComObject Scripting.FileSystemObject).GetFolder("C:\Program Files\Microsoft\jdk-17.x.x").ShortPath` to find yours.

### 3 — Download dataset and preprocess

```powershell
python notebooks/explore_data.py      # visualise raw data
python backend/preprocessing.py       # creates data/X_train.npy, X_test.npy
```

### 4 — Train the model

```powershell
python backend/train.py
# Saves: models/lstm_ae.h5, models/scaler.pkl
# Training takes 10–30 min depending on hardware
```

### 5 — Run anomaly detection

```powershell
python backend/anomaly.py
# Saves: data/anomaly_results.csv
```

### 6 — Install React dependencies

```powershell
cd frontend/dashboard
npm install
cd ../..
```

---

## Running the Full System

Open **6 terminal windows** and run one command in each:

```powershell
# Window 1 — ZooKeeper (Kafka coordinator)
cd C:\tools\kafka
.\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties

# Window 2 — Kafka Broker
cd C:\tools\kafka
.\bin\windows\kafka-server-start.bat .\config\server.properties

# Window 3 — Kafka Producer (streams sensor data)
cd C:\anomaly_detection
.\venv\Scripts\Activate.ps1
# set env vars (see Installation step 2)
python kafka/producer.py

# Window 4 — Spark Stream Processor
cd C:\anomaly_detection
.\venv\Scripts\Activate.ps1
# set env vars
python spark/stream_processor.py

# Window 5 — FastAPI Backend
cd C:\anomaly_detection
.\venv\Scripts\Activate.ps1
uvicorn backend.api:app --reload --port 8000

# Window 6 — React Dashboard
cd C:\anomaly_detection\frontend\dashboard
npm run dev
```

**Start order matters:** ZooKeeper → Kafka → Producer → Spark → Backend → Frontend

| Service | URL |
|---|---|
| React Dashboard | http://localhost:5173 |
| FastAPI (Swagger UI) | http://localhost:8000/docs |
| Airflow UI | http://localhost:8080 |

---

## Airflow Pipeline

Copy the DAG to Airflow's dags folder (in WSL):

```bash
cp /mnt/c/anomaly_detection/airflow_dags/anomaly_pipeline.py ~/airflow/dags/
```

The pipeline runs daily and executes 4 tasks in sequence:

```
ingest_data → preprocess_data → train_model → run_predictions
```

View and trigger runs at `http://localhost:8080` (login: `admin` / `admin`).

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Check if model and results are loaded |
| `GET` | `/anomalies?limit=1000` | Return all anomaly detection results |
| `POST` | `/predict` | Predict on a single 50-value sequence |
| `WS` | `/stream` | WebSocket — live Kafka data push to React |

**Example `/predict` request:**
```json
POST http://localhost:8000/predict
{
  "sequence": [57.6, 57.2, 56.9, 57.8, 58.1, ...]
}
```

**Response:**
```json
{
  "reconstruction_error": 0.000423,
  "threshold": 0.001872,
  "is_anomaly": false
}
```

---

## Common Issues

| Error | Cause | Fix |
|---|---|---|
| `WinError 2` on Spark start | Wrong `SPARK_HOME` or `JAVA_HOME` | Set `SPARK_HOME=C:\tools\spark`, use short path for `JAVA_HOME` |
| `UnsatisfiedLinkError: NativeIO$Windows` | Wrong or missing `winutils.exe` / `hadoop.dll` | Download hadoop-3.3.6 versions, copy `hadoop.dll` to `C:\Windows\System32` |
| `ModuleNotFoundError: model` | Running uvicorn from wrong directory | Add `sys.path.insert(0, os.path.dirname(__file__))` to `api.py` |
| Kafka `Connection refused` | Broker not running | Start ZooKeeper first, then broker |
| Airflow `command not found` | `~/.local/bin` not in PATH | Run `echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc && source ~/.bashrc` |
| Empty Spark batches | Producer not running | Start `kafka/producer.py` in a separate window |

---

## Resume / Interview Summary

**Problem solved:** Automated detection of anomalous behaviour in industrial sensor streams without requiring manually labelled training data.

**How it works:** An LSTM Autoencoder is trained exclusively on normal sensor readings. Because it has never seen anomalous patterns, its reconstruction error spikes when anomalies appear — that spike is the detection signal. The 95th-percentile error threshold is used to flag the top 5% most unusual sequences.

**Why unsupervised?** In real production systems, labelled anomaly data is rare and expensive. Unsupervised detection generalises to new failure modes the system has never encountered.

**Scale:** Kafka + Spark means the architecture can handle millions of events per second by adding more brokers and executors — the ML logic doesn't change.

---

## License

MIT
