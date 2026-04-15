// App.jsx — root component, assembles the full dashboard
import { useState, useEffect } from "react";
import NavBar from "./components/NavBar";
import LiveChart from "./components/LiveChart";
import StatusCard from "./components/StatusCard";
import AnomalyTable from "./components/AnomalyTable";
import { useWebSocket } from "./hooks/useWebSocket";
import { fetchAnomalies, fetchHealth } from "./api";

export default function App() {
    const [anomalyData, setAnomalyData]   = useState(null);
    const [health, setHealth]             = useState(null);
    const [loadError, setLoadError]       = useState(null);

    const { dataPoints, isConnected } = useWebSocket(
        "ws://localhost:8000/stream", 200
    );

    // Load anomaly results and health on first render
    useEffect(() => {
        fetchAnomalies()
            .then(setAnomalyData)
            .catch(e => setLoadError(e.message));

        fetchHealth()
            .then(setHealth)
            .catch(() => setHealth({ status: "unreachable" }));
    }, []);

    const liveAnomalies = dataPoints.filter(d => d.is_anomaly).length;
    const backendOnline = health?.status === "ok";

    return (
        <div style={{ fontFamily: "'Segoe UI', system-ui, sans-serif",
                      background: "#f8fafc", minHeight: "100vh" }}>

            <NavBar isConnected={isConnected}
                    anomalyCount={liveAnomalies} />

            <div style={{ maxWidth: "1200px", margin: "0 auto",
                          padding: "1.5rem" }}>

                {/* Error banner */}
                {loadError && (
                    <div style={{ background: "#fef2f2", border: "1px solid #fecaca",
                                  color: "#dc2626", padding: "12px 16px",
                                  borderRadius: "8px", marginBottom: "1.5rem",
                                  fontSize: "13px" }}>
                        ⚠ Could not reach backend: {loadError}.
                        Make sure <code>uvicorn backend.api:app --port 8000</code> is running.
                    </div>
                )}

                {/* Summary cards */}
                <div style={{ display: "flex", gap: "12px",
                              marginBottom: "1.5rem", flexWrap: "wrap" }}>
                    <StatusCard
                        title="Total sequences"
                        value={anomalyData?.total_sequences?.toLocaleString() ?? "—"}
                        color="#0f172a"
                    />
                    <StatusCard
                        title="Anomalies found"
                        value={anomalyData?.total_anomalies?.toLocaleString() ?? "—"}
                        color="#dc2626"
                        subtitle="in stored results"
                    />
                    <StatusCard
                        title="Threshold"
                        value={anomalyData?.threshold?.toFixed(4) ?? "—"}
                        color="#f97316"
                        subtitle="95th percentile"
                    />
                    <StatusCard
                        title="Live points"
                        value={dataPoints.length}
                        color="#0ea5e9"
                    />
                    <StatusCard
                        title="Live anomalies"
                        value={liveAnomalies}
                        color={liveAnomalies > 0 ? "#dc2626" : "#16a34a"}
                        subtitle="in current window"
                    />
                    <StatusCard
                        title="Backend"
                        value={backendOnline ? "Online" : "Offline"}
                        color={backendOnline ? "#16a34a" : "#dc2626"}
                        subtitle={health?.model_loaded ? "model loaded" : "model not loaded"}
                    />
                </div>

                {/* Live chart */}
                <div style={{ marginBottom: "1.5rem" }}>
                    <LiveChart dataPoints={dataPoints} />
                </div>

                {/* Anomaly table */}
                <AnomalyTable data={anomalyData?.data} />

            </div>
        </div>
    );
}