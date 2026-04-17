export default function AnomalyTable({ data }) {
    const anomalies = (data || []).filter(d => d.is_anomaly).slice(-20).reverse();

    return (
        <div style={{ background: "white", borderRadius: "12px",
                      border: "0.5px solid #e2e8f0", padding: "1.25rem" }}>
            <h2 style={{ margin: "0 0 1rem", fontSize: "15px", fontWeight: 600 }}>
                Detected Anomalies
                <span style={{ marginLeft: "8px", background: "#fef2f2", color: "#dc2626",
                               fontSize: "11px", padding: "2px 8px", borderRadius: "10px" }}>
                    {anomalies.length} shown
                </span>
            </h2>
            {anomalies.length === 0
                ? <p style={{ color: "#94a3b8", fontSize: "13px" }}>No anomalies yet.</p>
                : <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
                    <thead>
                        <tr style={{ borderBottom: "1px solid #f1f5f9" }}>
                            {["Sequence #","Recon. Error","Threshold","Status"].map(h => (
                                <th key={h} style={{ padding: "8px 12px", textAlign: "left",
                                                     color: "#94a3b8", fontWeight: 500,
                                                     fontSize: "11px" }}>{h}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {anomalies.map((row, i) => (
                            <tr key={i} style={{ borderBottom: "0.5px solid #f8fafc" }}>
                                <td style={{ padding: "10px 12px", fontFamily: "monospace" }}>
                                    {row.sequence_index ?? i}</td>
                                <td style={{ padding: "10px 12px", color: "#dc2626",
                                             fontFamily: "monospace" }}>
                                    {Number(row.reconstruction_error).toFixed(5)}</td>
                                <td style={{ padding: "10px 12px", fontFamily: "monospace",
                                             color: "#64748b" }}>
                                    {Number(row.threshold).toFixed(5)}</td>
                                <td style={{ padding: "10px 12px" }}>
                                    <span style={{ background: "#fef2f2", color: "#dc2626",
                                                   border: "1px solid #fecaca",
                                                   padding: "2px 8px", borderRadius: "4px",
                                                   fontSize: "11px" }}>ANOMALY</span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                  </table>
            }
        </div>
    );
}
