/**
 * Real-time stock data hook with automatic fallback to REST polling
 * if WebSocket/Kafka streaming fails.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { getStockQuote, StockQuote } from './api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface StockPriceUpdate {
  symbol: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  timestamp: string;
}

interface UseStockStreamOptions {
  symbols: string[];
  fallbackPollingInterval?: number; // ms, default 10000 (10 seconds)
  maxReconnectAttempts?: number;
  onError?: (error: Error) => void;
}

interface UseStockStreamResult {
  prices: Map<string, StockPriceUpdate>;
  isConnected: boolean;
  isUsingFallback: boolean;
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'fallback';
  reconnect: () => void;
}

export function useStockStream({
  symbols,
  fallbackPollingInterval = 10000,
  maxReconnectAttempts = 3,
  onError,
}: UseStockStreamOptions): UseStockStreamResult {
  const [prices, setPrices] = useState<Map<string, StockPriceUpdate>>(new Map());
  const [isConnected, setIsConnected] = useState(false);
  const [isUsingFallback, setIsUsingFallback] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'fallback'>('connecting');
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const mountedRef = useRef(true);

  // Fallback: Poll REST API for stock prices
  const pollStockPrices = useCallback(async () => {
    if (!mountedRef.current) return;
    
    try {
      const updates = await Promise.all(
        symbols.map(async (symbol) => {
          try {
            const quote = await getStockQuote(symbol);
            return {
              symbol,
              price: parseFloat(quote.price),
              change: parseFloat(quote.change),
              change_percent: parseFloat(quote.change_percent),
              volume: quote.volume,
              timestamp: new Date().toISOString(),
            };
          } catch {
            return null;
          }
        })
      );

      if (!mountedRef.current) return;

      setPrices((prev) => {
        const newPrices = new Map(prev);
        updates.forEach((update) => {
          if (update) {
            newPrices.set(update.symbol, update);
          }
        });
        return newPrices;
      });
    } catch (error) {
      console.error('Fallback polling error:', error);
      onError?.(error instanceof Error ? error : new Error('Polling failed'));
    }
  }, [symbols, onError]);

  // Start fallback polling
  const startFallbackPolling = useCallback(() => {
    if (pollingIntervalRef.current) return; // Already polling
    
    console.log('Starting fallback REST polling...');
    setIsUsingFallback(true);
    setConnectionStatus('fallback');
    
    // Initial fetch
    pollStockPrices();
    
    // Set up interval
    pollingIntervalRef.current = setInterval(pollStockPrices, fallbackPollingInterval);
  }, [pollStockPrices, fallbackPollingInterval]);

  // Stop fallback polling
  const stopFallbackPolling = useCallback(() => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
    setIsUsingFallback(false);
  }, []);

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (!mountedRef.current) return;
    
    // Close existing connection
    if (wsRef.current) {
      wsRef.current.close();
    }

    setConnectionStatus('connecting');
    
    try {
      const wsUrl = API_BASE_URL.replace('http', 'ws');
      const ws = new WebSocket(`${wsUrl}/api/v1/stocks/ws/stream`);
      wsRef.current = ws;

      ws.onopen = () => {
        if (!mountedRef.current) return;
        
        console.log('WebSocket connected');
        setIsConnected(true);
        setConnectionStatus('connected');
        reconnectAttemptsRef.current = 0;
        
        // Stop fallback if it was running
        stopFallbackPolling();
        
        // Subscribe to symbols
        ws.send(JSON.stringify({ type: 'subscribe', symbols }));
      };

      ws.onmessage = (event) => {
        if (!mountedRef.current) return;
        
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'price_update' || data.symbol) {
            const update: StockPriceUpdate = {
              symbol: data.symbol,
              price: data.price,
              change: data.change || 0,
              change_percent: data.change_percent || 0,
              volume: data.volume || 0,
              timestamp: data.timestamp || new Date().toISOString(),
            };
            
            setPrices((prev) => {
              const newPrices = new Map(prev);
              newPrices.set(update.symbol, update);
              return newPrices;
            });
          }
        } catch (error) {
          console.error('WebSocket message parse error:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        onError?.(new Error('WebSocket connection error'));
      };

      ws.onclose = () => {
        if (!mountedRef.current) return;
        
        console.log('WebSocket closed');
        setIsConnected(false);
        wsRef.current = null;
        
        // Attempt reconnection
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          console.log(`Reconnection attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts}`);
          setConnectionStatus('connecting');
          
          // Exponential backoff
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 10000);
          setTimeout(connect, delay);
        } else {
          console.log('Max reconnection attempts reached, switching to fallback');
          startFallbackPolling();
        }
      };
    } catch (error) {
      console.error('WebSocket connection failed:', error);
      startFallbackPolling();
    }
  }, [symbols, maxReconnectAttempts, onError, stopFallbackPolling, startFallbackPolling]);

  // Manual reconnect
  const reconnect = useCallback(() => {
    reconnectAttemptsRef.current = 0;
    stopFallbackPolling();
    connect();
  }, [connect, stopFallbackPolling]);

  // Effect: Connect on mount
  useEffect(() => {
    mountedRef.current = true;
    connect();

    return () => {
      mountedRef.current = false;
      if (wsRef.current) {
        wsRef.current.close();
      }
      stopFallbackPolling();
    };
  }, [connect, stopFallbackPolling]);

  // Effect: Update subscription when symbols change
  useEffect(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'subscribe', symbols }));
    }
  }, [symbols]);

  return {
    prices,
    isConnected,
    isUsingFallback,
    connectionStatus,
    reconnect,
  };
}

// Simple hook for single stock with fallback
export function useStockPrice(symbol: string): {
  price: StockPriceUpdate | null;
  isLoading: boolean;
  error: Error | null;
  isUsingFallback: boolean;
} {
  const [price, setPrice] = useState<StockPriceUpdate | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  
  const { prices, isUsingFallback } = useStockStream({
    symbols: [symbol],
    onError: setError,
  });

  useEffect(() => {
    const update = prices.get(symbol);
    if (update) {
      setPrice(update);
      setIsLoading(false);
    }
  }, [prices, symbol]);

  return { price, isLoading, error, isUsingFallback };
}
