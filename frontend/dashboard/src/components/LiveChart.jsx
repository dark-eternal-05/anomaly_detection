import { Chart as ChartJS, LineElement, PointElement, LinearScale,
         CategoryScale, Tooltip, Legend, Filler } from "chart.js";
import { Line } from "react-chartjs-2";
ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, Tooltip, Legend, Filler);

export default function LiveChart({ dataPoints }) {
    const labels = dataPoints.map(d => d.timestamp ? String(d.timestamp).slice(11,19) : "");
    const values = dataPoints.map(d => d.value);
    const colors = dataPoints.map(d => d.is_anomaly ? "#ef4444" : "#3b82f6");
    const radii  = dataPoints.map(d => d.is_anomaly ? 7 : 2);

    const data = {
        labels,
        datasets: [{ label: "Sensor value", data: values,
                     borderColor: "#3b82f6", borderWidth: 1.5,
                     pointBackgroundColor: colors, pointRadius: radii,
                     tension: 0.3, fill: true,
                     backgroundColor: "rgba(59,130,246,0.05)" }]
    };

    const options = {
        responsive: true, animation: false,
        scales: {
            x: { ticks: { maxTicksLimit: 8, font: { size: 11 }, color: "#94a3b8" },
                 grid: { display: false } },
            y: { ticks: { font: { size: 11 }, color: "#94a3b8" },
                 grid: { color: "#f1f5f9" } }
        },
        plugins: { legend: { display: false } }
    };

    return (
        <div style={{ background: "white", borderRadius: "12px",
                      border: "0.5px solid #e2e8f0", padding: "1.25rem" }}>
            <h2 style={{ margin: "0 0 1rem", fontSize: "15px", fontWeight: 600 }}>
                Live Sensor Stream
                <span style={{ marginLeft: "8px", fontSize: "12px",
                               color: "#94a3b8", fontWeight: 400 }}>
                    last {dataPoints.length} readings
                </span>
            </h2>
            {dataPoints.length === 0
                ? <div style={{ height: "240px", display: "flex", alignItems: "center",
                                justifyContent: "center", color: "#94a3b8" }}>
                    Waiting for data — is Kafka producer running?
                  </div>
                : <Line data={data} options={options} style={{ maxHeight: "280px" }} />
            }
        </div>
    );
}
