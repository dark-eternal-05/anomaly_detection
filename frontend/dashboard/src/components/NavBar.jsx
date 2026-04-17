export default function NavBar({ isConnected, anomalyCount }) {
    return (
        <nav style={{ background: "#0f172a", color: "white", padding: "0 1.5rem",
                      height: "56px", display: "flex", alignItems: "center",
                      justifyContent: "space-between", position: "sticky",
                      top: 0, zIndex: 100 }}>
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <div style={{ width: "28px", height: "28px",
                              background: "linear-gradient(135deg, #ef4444, #f97316)",
                              borderRadius: "6px", display: "flex",
                              alignItems: "center", justifyContent: "center",
                              fontSize: "14px", fontWeight: 700 }}>A</div>
                <span style={{ fontWeight: 600, fontSize: "15px" }}>AnomalyWatch</span>
                <span style={{ color: "#64748b", fontSize: "13px" }}>Real-Time Detection</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                {anomalyCount > 0 && (
                    <div style={{ background: "#fef2f2", color: "#dc2626",
                                  border: "1px solid #fecaca", borderRadius: "20px",
                                  padding: "3px 10px", fontSize: "12px" }}>
                        ? {anomalyCount} anomalies
                    </div>
                )}
                <div style={{ display: "flex", alignItems: "center", gap: "6px",
                              fontSize: "12px", color: isConnected ? "#4ade80" : "#f87171" }}>
                    <div style={{ width: "7px", height: "7px", borderRadius: "50%",
                                  background: isConnected ? "#4ade80" : "#f87171" }}/>
                    {isConnected ? "Live" : "Disconnected"}
                </div>
            </div>
        </nav>
    );
}
