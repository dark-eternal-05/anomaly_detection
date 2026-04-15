// AnomalyTable.jsx — table of detected anomalies from the backend
export default function AnomalyTable({ data }) {
    // filter to anomalies only, take last 20
    const anomalies = (data || [])
        .filter(d => d.is_anomaly)
        .slice(-20)
        .reverse();   // newest first

    if (anomalies.length === 0) return (
        <div style={{ background: "white", borderRadius: "12px",
                      border: "0.5px solid #e2e8f0", padding: "1.25rem" }}>
            <h2 style={{ margin: "0 0 0.5rem", fontSize: "15px", fontWeight: 600 }}>
                Detected Anomalies
            </h2>
            <p style={{ color: "#94a3b8", fontSize: "13px" }}>
                No anomalies detected yet.
            </p>
        </div>
    );

    return (
        <div style={{ background: "white", borderRadius: "12px",
                      border: "0.5px solid #e2e8f0", padding: "1.25rem" }}>
            <h2 style={{ margin: "0 0 1rem", fontSize: "15px", fontWeight: 600,
                         color: "#0f172a" }}>
                Detected Anomalies
                <span style={{ marginLeft: "8px", background: "#fef2f2", color: "#dc2626",
                               fontSize: "11px", padding: "2px 8px", borderRadius: "10px",
                               fontWeight: 500 }}>
                    {anomalies.length} shown
                </span>
            </h2>
            <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse",
                                fontSize: "13px" }}>
                    <thead>
                        <tr style={{ borderBottom: "1px solid #f1f5f9" }}>
                            {["Sequence #", "Recon. Error", "Threshold", "Status"].map(h => (
                                <th key={h} style={{ padding: "8px 12px", textAlign: "left",
                                                     color: "#94a3b8", fontWeight: 500,
                                                     fontSize: "11px", textTransform: "uppercase",
                                                     letterSpacing: "0.05em" }}>
                                    {h}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {anomalies.map((row, i) => (
                            <tr key={i} style={{ borderBottom: "0.5px solid #f8fafc" }}>
                                <td style={{ padding: "10px 12px", color: "#475569",
                                             fontFamily: "monospace" }}>
                                    {row.sequence_index ?? i}
                                </td>
                                <td style={{ padding: "10px 12px", color: "#dc2626",
                                             fontFamily: "monospace", fontWeight: 500 }}>
                                    {Number(row.reconstruction_error).toFixed(5)}
                                </td>
                                <td style={{ padding: "10px 12px", color: "#64748b",
                                             fontFamily: "monospace" }}>
                                    {Number(row.threshold).toFixed(5)}
                                </td>
                                <td style={{ padding: "10px 12px" }}>
                                    <span style={{
                                        background: "#fef2f2", color: "#dc2626",
                                        border: "1px solid #fecaca",
                                        padding: "2px 8px", borderRadius: "4px",
                                        fontSize: "11px", fontWeight: 500
                                    }}>
                                        ANOMALY
                                    </span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}