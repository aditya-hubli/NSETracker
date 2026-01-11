'use client';

import { useState, useEffect } from 'react';
import { PriceAlert, Notification as NotificationType } from '@/lib/api';

interface AlertFormProps {
  symbol: string;
  currentPrice: number;
  onSubmit: (data: {
    condition: 'above' | 'below' | 'percent_up' | 'percent_down';
    target_value: number;
    message?: string;
  }) => void;
}

export function AlertForm({ symbol, currentPrice, onSubmit }: AlertFormProps) {
  const [condition, setCondition] = useState<'above' | 'below' | 'percent_up' | 'percent_down'>('above');
  const [targetValue, setTargetValue] = useState<string>(currentPrice.toFixed(2));
  const [message, setMessage] = useState<string>('');
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      condition,
      target_value: parseFloat(targetValue),
      message: message || undefined,
    });
  };
  
  const isPercentage = condition === 'percent_up' || condition === 'percent_down';
  
  return (
    <form onSubmit={handleSubmit} className="bg-gray-800 rounded-lg border border-gray-700 p-4">
      <h3 className="font-semibold text-white mb-4">Create Price Alert for {symbol}</h3>
      <p className="text-sm text-gray-400 mb-4">Current Price: ${currentPrice.toFixed(2)}</p>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm text-gray-400 mb-1">Alert Condition</label>
          <select 
            value={condition}
            onChange={(e) => setCondition(e.target.value as typeof condition)}
            className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
          >
            <option value="above">Price goes above</option>
            <option value="below">Price goes below</option>
            <option value="percent_up">Price increases by %</option>
            <option value="percent_down">Price decreases by %</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm text-gray-400 mb-1">
            Target {isPercentage ? 'Percentage' : 'Price'}
          </label>
          <div className="relative">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
              {isPercentage ? '%' : '$'}
            </span>
            <input
              type="number"
              step={isPercentage ? '0.1' : '0.01'}
              value={targetValue}
              onChange={(e) => setTargetValue(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 pl-8 text-white"
              required
            />
          </div>
        </div>
        
        <div>
          <label className="block text-sm text-gray-400 mb-1">Custom Message (optional)</label>
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="e.g., Time to sell!"
            className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
          />
        </div>
        
        <button
          type="submit"
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded transition-colors"
        >
          Create Alert
        </button>
      </div>
    </form>
  );
}

interface AlertListProps {
  alerts: PriceAlert[];
  onCancel: (alertId: string) => void;
}

export function AlertList({ alerts, onCancel }: AlertListProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-blue-400';
      case 'triggered': return 'text-green-400';
      case 'expired': return 'text-gray-500';
      case 'cancelled': return 'text-gray-500';
      default: return 'text-gray-400';
    }
  };
  
  const getConditionText = (alert: PriceAlert) => {
    switch (alert.condition) {
      case 'above': return `> $${alert.target_value.toFixed(2)}`;
      case 'below': return `< $${alert.target_value.toFixed(2)}`;
      case 'percent_up': return `↑ ${alert.target_value}%`;
      case 'percent_down': return `↓ ${alert.target_value}%`;
    }
  };
  
  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700">
      <div className="px-4 py-3 border-b border-gray-700">
        <h3 className="font-semibold text-white">Your Alerts</h3>
      </div>
      
      {alerts.length === 0 ? (
        <div className="p-8 text-center text-gray-500">
          No alerts set. Create one to get notified!
        </div>
      ) : (
        <div className="divide-y divide-gray-700">
          {alerts.map((alert) => (
            <div key={alert.id} className="px-4 py-3 flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-medium text-white">{alert.symbol}</span>
                  <span className="text-sm text-gray-400">{getConditionText(alert)}</span>
                </div>
                <div className="flex items-center gap-2 mt-1">
                  <span className={`text-xs ${getStatusColor(alert.status)}`}>
                    {alert.status.toUpperCase()}
                  </span>
                  {alert.message && (
                    <span className="text-xs text-gray-500">"{alert.message}"</span>
                  )}
                </div>
              </div>
              {alert.status === 'active' && (
                <button
                  onClick={() => onCancel(alert.id)}
                  className="text-red-400 hover:text-red-300 text-sm"
                >
                  Cancel
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

interface NotificationBellProps {
  unreadCount: number;
  onClick: () => void;
}

export function NotificationBell({ unreadCount, onClick }: NotificationBellProps) {
  return (
    <button 
      onClick={onClick}
      className="relative p-2 text-gray-400 hover:text-white transition-colors"
    >
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
      </svg>
      {unreadCount > 0 && (
        <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs w-5 h-5 rounded-full flex items-center justify-center">
          {unreadCount > 9 ? '9+' : unreadCount}
        </span>
      )}
    </button>
  );
}

interface NotificationListProps {
  notifications: NotificationType[];
  onMarkRead: (id: string) => void;
  onMarkAllRead: () => void;
}

export function NotificationList({ notifications, onMarkRead, onMarkAllRead }: NotificationListProps) {
  const getIcon = (type: string) => {
    switch (type) {
      case 'price_alert': return '●';
      case 'price_change': return '▲';
      case 'volume_spike': return '■';
      case 'sentiment_shift': return '◆';
      case 'signal_change': return '⚡';
      case 'news_alert': return '□';
      default: return '●';
    }
  };
  
  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 max-h-96 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-700 flex justify-between items-center sticky top-0 bg-gray-800">
        <h3 className="font-semibold text-white">Notifications</h3>
        {notifications.some(n => !n.read) && (
          <button 
            onClick={onMarkAllRead}
            className="text-xs text-blue-400 hover:text-blue-300"
          >
            Mark all read
          </button>
        )}
      </div>
      
      {notifications.length === 0 ? (
        <div className="p-8 text-center text-gray-500">
          No notifications yet
        </div>
      ) : (
        <div className="divide-y divide-gray-700 overflow-y-auto max-h-80">
          {notifications.map((notification) => (
            <div 
              key={notification.id}
              className={`px-4 py-3 cursor-pointer transition-colors ${
                notification.read ? 'bg-gray-800' : 'bg-gray-700/50'
              } hover:bg-gray-700`}
              onClick={() => !notification.read && onMarkRead(notification.id)}
            >
              <div className="flex items-start gap-3">
                <span className="text-xl">{getIcon(notification.type)}</span>
                <div className="flex-1 min-w-0">
                  <p className={`text-sm ${notification.read ? 'text-gray-400' : 'text-white font-medium'}`}>
                    {notification.title}
                  </p>
                  <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                    {notification.message}
                  </p>
                  <p className="text-xs text-gray-600 mt-1">
                    {new Date(notification.created_at).toLocaleString()}
                  </p>
                </div>
                {!notification.read && (
                  <span className="w-2 h-2 bg-blue-500 rounded-full shrink-0 mt-2" />
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

interface RealTimeUpdatesProps {
  userId: string;
  onPriceUpdate?: (data: { symbol: string; price: number; change_percent: number }) => void;
  onNotification?: (notification: NotificationType) => void;
}

export function useRealTimeUpdates({ userId, onPriceUpdate, onNotification }: RealTimeUpdatesProps) {
  const [connected, setConnected] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);
  
  useEffect(() => {
    const wsUrl = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace('http', 'ws');
    const socket = new WebSocket(`${wsUrl}/api/v1/notifications/ws/${userId}`);
    
    socket.onopen = () => {
      setConnected(true);
      console.log('WebSocket connected');
    };
    
    socket.onclose = () => {
      setConnected(false);
      console.log('WebSocket disconnected');
    };
    
    socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        
        if (message.event === 'price_update' && onPriceUpdate) {
          onPriceUpdate(message.data);
        } else if (message.event === 'notification' && onNotification) {
          onNotification(message.data);
        } else if (message.event === 'alert_triggered' && onNotification) {
          onNotification(message.data);
        }
      } catch (e) {
        console.error('Error parsing WebSocket message:', e);
      }
    };
    
    setWs(socket);
    
    return () => {
      socket.close();
    };
  }, [userId]);
  
  const subscribe = (symbols: string[]) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ event: 'subscribe', data: { symbols } }));
    }
  };
  
  const unsubscribe = (symbols: string[]) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ event: 'unsubscribe', data: { symbols } }));
    }
  };
  
  return { connected, subscribe, unsubscribe };
}
