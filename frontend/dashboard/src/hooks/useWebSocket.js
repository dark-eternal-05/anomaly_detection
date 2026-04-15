// useWebSocket.js — manages a persistent WebSocket connection
// Appends incoming messages to a rolling window of maxPoints
import { useState, useEffect, useRef } from "react";

export function useWebSocket(url, maxPoints = 200) {
    const [dataPoints, setDataPoints] = useState([]);
    const [isConnected, setIsConnected] = useState(false);
    const [error, setError] = useState(null);
    const wsRef = useRef(null);

    useEffect(() => {
        let ws;
        let reconnectTimer;

        const connect = () => {
            ws = new WebSocket(url);
            wsRef.current = ws;

            ws.onopen = () => {
                setIsConnected(true);
                setError(null);
                console.log("WebSocket connected");
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                setDataPoints(prev => [...prev, data].slice(-maxPoints));
            };

            ws.onclose = () => {
                setIsConnected(false);
                // Auto-reconnect after 3 seconds
                reconnectTimer = setTimeout(connect, 3000);
            };

            ws.onerror = () => {
                setError("WebSocket error — is the backend running?");
                ws.close();
            };
        };

        connect();

        return () => {
            clearTimeout(reconnectTimer);
            ws?.close();
        };
    }, [url, maxPoints]);

    return { dataPoints, isConnected, error };
}
