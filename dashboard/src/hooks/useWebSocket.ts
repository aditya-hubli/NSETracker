'use client';

import { useEffect, useRef, useState, useCallback } from 'react';

export interface PriceUpdate {
  symbol: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  timestamp?: string;
}

export interface WebSocketMessage {
  event: string;
  data: Record<string, unknown>;
}

export interface UseWebSocketOptions {
  userId?: string;
  autoConnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  lastMessage: WebSocketMessage | null;
  priceUpdates: Record<string, number>;
  subscribe: (symbols: string | string[]) => void;
  unsubscribe: (symbols: string | string[]) => void;
  connect: () => void;
  disconnect: () => void;
}

export function useWebSocket(options?: UseWebSocketOptions): UseWebSocketReturn {
  const {
    userId = `user-${Date.now()}`,
    autoConnect = true,
    reconnectInterval = 5000,
    maxReconnectAttempts = 5,
  } = options || {};
  
  const hasLoggedStatus = useRef(false);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [priceUpdates, setPriceUpdates] = useState<Record<string, number>>({});
  const [subscribedSymbols, setSubscribedSymbols] = useState<Set<string>>(new Set());

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    try {
      const ws = new WebSocket(`ws://localhost:8000/api/v1/notifications/ws/${userId}`);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected - real-time updates enabled');
        setIsConnected(true);
        reconnectAttemptsRef.current = 0;
        hasLoggedStatus.current = false;

        // Resubscribe to previously subscribed symbols
        if (subscribedSymbols.size > 0) {
          ws.send(JSON.stringify({
            event: 'subscribe',
            data: { symbols: Array.from(subscribedSymbols) }
          }));
        }
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          setLastMessage(message);

          // Handle price updates
          if (message.event === 'price_update') {
            const data = message.data as { symbol: string; price: number };
            setPriceUpdates(prev => ({
              ...prev,
              [data.symbol]: data.price,
            }));
          }
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.onerror = () => {
        // Only log once to avoid console spam
        if (!hasLoggedStatus.current) {
          hasLoggedStatus.current = true;
          console.log('WebSocket connecting...');
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        wsRef.current = null;

        // Attempt to reconnect silently
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        }
      };
    } catch (err) {
      console.error('Failed to connect WebSocket:', err);
    }
  }, [userId, reconnectInterval, maxReconnectAttempts, subscribedSymbols]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setIsConnected(false);
    reconnectAttemptsRef.current = maxReconnectAttempts; // Prevent auto-reconnect
  }, [maxReconnectAttempts]);

  const subscribe = useCallback((symbols: string | string[]) => {
    const symbolArray = Array.isArray(symbols) ? symbols : [symbols];
    const newSymbols = symbolArray.map(s => s.toUpperCase());
    setSubscribedSymbols(prev => {
      const updated = new Set(prev);
      newSymbols.forEach(s => updated.add(s));
      return updated;
    });

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        event: 'subscribe',
        data: { symbols: newSymbols }
      }));
    }
  }, []);

  const unsubscribe = useCallback((symbols: string | string[]) => {
    const symbolArray = Array.isArray(symbols) ? symbols : [symbols];
    const removeSymbols = symbolArray.map(s => s.toUpperCase());
    setSubscribedSymbols(prev => {
      const updated = new Set(prev);
      removeSymbols.forEach(s => updated.delete(s));
      return updated;
    });

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        event: 'unsubscribe',
        data: { symbols: removeSymbols }
      }));
    }

    // Remove from price updates
    setPriceUpdates(prev => {
      const updated = { ...prev };
      removeSymbols.forEach(s => delete updated[s]);
      return updated;
    });
  }, []);

  // Auto-connect on mount or when userId changes
  useEffect(() => {
    if (autoConnect && userId) {
      // Disconnect existing connection if userId changed
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, userId]); // eslint-disable-line react-hooks/exhaustive-deps

  return {
    isConnected,
    lastMessage,
    priceUpdates,
    subscribe,
    unsubscribe,
    connect,
    disconnect,
  };
}

export default useWebSocket;
