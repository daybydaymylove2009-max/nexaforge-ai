import { useState, useEffect, useCallback, useRef } from 'react';

export function useHardwareWebSocket(url) {
  const [data, setData] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const ws = useRef(null);
  const reconnectTimeout = useRef(null);

  const connect = useCallback(() => {
    try {
      if (ws.current?.readyState === WebSocket.OPEN) return;
      
      const wsUrl = url.startsWith('http') ? url.replace('http', 'ws') : url;
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        setIsConnected(true);
        setError(null);
        console.log('✅ WebSocket Connected');
      };

      ws.current.onmessage = (event) => {
        try {
          const parsedData = JSON.parse(event.data);
          setData(parsedData);
        } catch (err) {
          console.error('Failed to parse WebSocket message', err);
        }
      };

      ws.current.onclose = () => {
        setIsConnected(false);
        console.log('❌ WebSocket Disconnected');
        // Auto reconnect
        reconnectTimeout.current = setTimeout(connect, 3000);
      };

      ws.current.onerror = (err) => {
        console.error('WebSocket Error:', err);
        setError('WebSocket Connection Error');
        ws.current.close();
      };
    } catch (err) {
      setError(err.message);
    }
  }, [url]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
      if (ws.current) ws.current.close();
    };
  }, [connect]);

  return { data, isConnected, error };
}
