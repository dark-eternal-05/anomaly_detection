// StatusCard.jsx — a single summary metric (title + big number)
export default function StatusCard({ title, value, color = "#0d6efd", subtitle }) {
    return (
        <div style={{
            background: "white",
            border: "0.5px solid #e0e0e0",
            borderRadius: "10px",
            padding: "1rem 1.25rem",
            textAlign: "center",
            flex: 1,
            minWidth: "130px",
            boxShadow: "0 1px 3px rgba(0,0,0,0.05)"
        }}>
            <div style={{ fontSize: "12px", color: "#888", marginBottom: "6px",
                          textTransform: "uppercase", letterSpacing: "0.05em" }}>
                {title}
            </div>
            <div style={{ fontSize: "26px", fontWeight: 600, color, lineHeight: 1 }}>
                {value}
            </div>
            {subtitle && (
                <div style={{ fontSize: "11px", color: "#aaa", marginTop: "4px" }}>
                    {subtitle}
                </div>
            )}
        </div>
    );
}