const BASE_URL = "http://localhost:8000";

export const fetchAnomalies = async (limit = 5000) => {
    const response = await fetch(`${BASE_URL}/anomalies?limit=${limit}`);
    if (!response.ok) throw new Error("Failed to fetch anomalies");
    return response.json();
};

export const fetchHealth = async () => {
    const response = await fetch(`${BASE_URL}/health`);
    if (!response.ok) throw new Error("Backend unreachable");
    return response.json();
};
