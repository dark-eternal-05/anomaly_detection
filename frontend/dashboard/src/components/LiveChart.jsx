// LiveChart.jsx — real-time line chart, anomalies shown as red dots
import {
    Chart as ChartJS, LineElement, PointElement,
    LinearScale, CategoryScale, Tooltip, Legend, Filler
} from "chart.js";
import { Line } from "react-chartjs-2";

ChartJS.register(LineElement, PointElement, LinearScale,
                 CategoryScale, Tooltip, Legend, Filler);

export default function LiveChart({ dataPoints }) {
    const labels = dataPoints.map(d =>
        d.timestamp ? String(d.timestamp).slice(11, 19) : ""
    );
    const values  = dataPoints.map(d => d.value);
    const colors  = dataPoints.map(d => d.is_anomaly ? "#ef4444" : "#3b82f6");
    const radii   = dataPoints.map(d => d.is_anomaly ? 7 : 2);
    const borders = dataPoints.map(d => d.is_anomaly ? "#ef4444" : "#3b82f6");

    const data = {
        labels,
        datasets: [{
            label: "Sensor value",
            data: values,
            borderColor: "#3b82f6",
            borderWidth: 1.5,
            pointBackgroundColor: colors,
            pointBorderColor: borders,
            pointRadius: radii,
            pointHoverRadius: 8,
            tension: 0.3,
            fill: true,
            backgroundColor: "rgba(59,130,246,0.05)",
        }]
    };

    const options = {
        responsive: true,
        animation: false,           // disabled for performance on live data
        interaction: { mode: "index", intersect: false },
        scales: {
            x: {
                ticks: { maxTicksLimit: 8, font: { size: 11 }, color: "#94a3b8" },
                grid: { display: false },
                border: { display: false }
            },
            y: {
                ticks: { font: { size: 11 }, color: "#94a3b8" },
                grid: { color: "#f1f5f9" },
                border: { display: false },
                title: { display: true, text: "Temperature", color: "#94a3b8",
                          font: { size: 11 } }
            }
        },
        plugins: {
            legend: { display: false },
            tooltip: {
                backgroundColor: "#0f172a",
                titleColor: "#e2e8f0",
                bodyColor: "#94a3b8",
                padding: 10,
                callbacks: {
                    afterBody: (items) => {
                        const d = dataPoints[items[0].dataIndex];
                        return d?.is_anomaly ? ["⚠  ANOMALY DETECTED"] : ["✓  Normal"];
                    }
                }
            }
        }
    };

    return (
        <div style={{ background: "white", borderRadius: "12px",
                      border: "0.5px solid #e2e8f0", padding: "1.25rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between",
                          alignItems: "center", marginBottom: "1rem" }}>
                <div>
                    <h2 style={{ margin: 0, fontSize: "15px", fontWeight: 600,
                                 color: "#0f172a" }}>Live Sensor Stream</h2>
                    <p style={{ margin: 0, fontSize: "12px", color: "#94a3b8" }}>
                        Last {dataPoints.length} readings
                    </p>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "16px",
                              fontSize: "12px", color: "#64748b" }}>
                    <span style={{ display: "flex", alignItems: "center", gap: "5px" }}>
                        <span style={{ width: "8px", height: "8px", borderRadius: "50%",
                                       background: "#3b82f6", display: "inline-block" }}/>
                        Normal
                    </span>
                    <span style={{ display: "flex", alignItems: "center", gap: "5px" }}>
                        <span style={{ width: "8px", height: "8px", borderRadius: "50%",
                                       background: "#ef4444", display: "inline-block" }}/>
                        Anomaly
                    </span>
                </div>
            </div>

            {dataPoints.length === 0 ? (
                <div style={{ height: "240px", display: "flex", alignItems: "center",
                              justifyContent: "center", color: "#94a3b8", fontSize: "14px" }}>
                    Waiting for data — is Kafka producer running?
                </div>
            ) : (
                <Line data={data} options={options} style={{ maxHeight: "280px" }} />
            )}
        </div>
    );
}