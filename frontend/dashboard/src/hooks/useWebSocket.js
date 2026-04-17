import { useState, useEffect, useRef } from "react";

export function useWebSocket(url, maxPoints = 200) {
    const [dataPoints, setDataPoints] = useState([]);
    const [isConnected, setIsConnected] = useState(false);
    const wsRef = useRef(null);

    useEffect(() => {
        let ws;
        let reconnectTimer;

        const connect = () => {
            ws = new WebSocket(url);
            wsRef.current = ws;
            ws.onopen = () => setIsConnected(true);
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                setDataPoints(prev => [...prev, data].slice(-maxPoints));
            };
            ws.onclose = () => {
                setIsConnected(false);
                reconnectTimer = setTimeout(connect, 3000);
            };
            ws.onerror = () => ws.close();
        };

        connect();
        return () => { clearTimeout(reconnectTimer); ws?.close(); };
    }, [url, maxPoints]);

    return { dataPoints, isConnected };
}
