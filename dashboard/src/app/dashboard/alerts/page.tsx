'use client';

import { useState, useEffect } from 'react';
import { searchStocks, SearchResult, getStockQuote } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';

interface PriceAlert {
  id: string;
  symbol: string;
  name: string;
  condition: 'above' | 'below' | 'percent_up' | 'percent_down';
  targetPrice: number;
  currentPrice: number;
  createdAt: string;
  triggered: boolean;
  notifyEmail: boolean;
  notifyPush: boolean;
  email?: string;
}

export default function AlertsPage() {
  const { user } = useAuth();
  const [alerts, setAlerts] = useState<PriceAlert[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [selectedStock, setSelectedStock] = useState<{ symbol: string; name: string; price: number } | null>(null);
  const [alertForm, setAlertForm] = useState({
    condition: 'above' as 'above' | 'below' | 'percent_up' | 'percent_down',
    targetPrice: '',
    notifyEmail: true,
    notifyPush: true,
  });

  // Load alerts from localStorage
  useEffect(() => {
    const savedAlerts = localStorage.getItem('priceAlerts');
    if (savedAlerts) {
      setAlerts(JSON.parse(savedAlerts));
    }
  }, []);

  // Save alerts to localStorage
  const saveAlerts = (updatedAlerts: PriceAlert[]) => {
    localStorage.setItem('priceAlerts', JSON.stringify(updatedAlerts));
    setAlerts(updatedAlerts);
  };

  // Search stocks
  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    if (query.length < 1) {
      setSearchResults([]);
      return;
    }
    setSearchLoading(true);
    try {
      const results = await searchStocks(query, false, 8);
      setSearchResults(results);
    } catch {
      setSearchResults([]);
    } finally {
      setSearchLoading(false);
    }
  };

  // Select stock for alert
  const selectStock = async (result: SearchResult) => {
    try {
      const quote = await getStockQuote(result.symbol);
      setSelectedStock({
        symbol: result.symbol,
        name: result.name,
        price: parseFloat(quote.price),
      });
      setSearchQuery('');
      setSearchResults([]);
    } catch (err) {
      console.error('Failed to get quote:', err);
    }
  };

  // Create alert
  const createAlert = () => {
    if (!selectedStock || !alertForm.targetPrice) return;

    // Use the authenticated user's email for notifications
    const userEmail = user?.email || '';

    const newAlert: PriceAlert = {
      id: Date.now().toString(),
      symbol: selectedStock.symbol,
      name: selectedStock.name,
      condition: alertForm.condition,
      targetPrice: parseFloat(alertForm.targetPrice),
      currentPrice: selectedStock.price,
      createdAt: new Date().toISOString(),
      triggered: false,
      notifyEmail: alertForm.notifyEmail,
      notifyPush: alertForm.notifyPush,
      email: userEmail,
    };

    saveAlerts([...alerts, newAlert]);
    setShowCreateModal(false);
    setSelectedStock(null);
    setAlertForm({
      condition: 'above',
      targetPrice: '',
      notifyEmail: true,
      notifyPush: true,
    });
  };

  // Delete alert
  const deleteAlert = (id: string) => {
    saveAlerts(alerts.filter((a) => a.id !== id));
  };

  // Format INR
  const formatINR = (value: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
    }).format(value);
  };

  // Get condition label
  const getConditionLabel = (condition: string, target: number) => {
    switch (condition) {
      case 'above':
        return `Price goes above ${formatINR(target)}`;
      case 'below':
        return `Price falls below ${formatINR(target)}`;
      case 'percent_up':
        return `Price increases by ${target}%`;
      case 'percent_down':
        return `Price decreases by ${target}%`;
      default:
        return '';
    }
  };

  const activeAlerts = alerts.filter((a) => !a.triggered);
  const triggeredAlerts = alerts.filter((a) => a.triggered);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Price Alerts</h1>
          <p className="text-gray-500 mt-1">Get notified when stocks hit your target price</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 text-white px-5 py-2.5 rounded-xl font-semibold transition shadow-lg shadow-emerald-500/30 flex items-center space-x-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          <span>Create Alert</span>
        </button>
      </div>

      {/* Active Alerts */}
      <div className="bg-white border border-gray-100 rounded-2xl shadow-sm overflow-hidden">
        <div className="p-5 border-b border-gray-100">
          <h2 className="text-lg font-semibold text-gray-900">Active Alerts ({activeAlerts.length})</h2>
        </div>
        {activeAlerts.length > 0 ? (
          <div className="divide-y divide-gray-100">
            {activeAlerts.map((alert) => (
              <div key={alert.id} className="p-5 flex justify-between items-center">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-emerald-500 to-green-600 rounded-xl flex items-center justify-center text-white font-bold">
                    {alert.symbol.replace('.NS', '').substring(0, 2)}
                  </div>
                  <div>
                    <div className="font-bold text-gray-900">
                      {alert.symbol.replace('.NS', '').replace('.BO', '')}
                    </div>
                    <div className="text-sm text-gray-500">{alert.name}</div>
                    <div className="text-sm text-emerald-600 mt-1">
                      {getConditionLabel(alert.condition, alert.targetPrice)}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <div className="text-sm text-gray-500">Current</div>
                    <div className="font-semibold text-gray-900">{formatINR(alert.currentPrice)}</div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {alert.notifyEmail && (
                      <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">Email</span>
                    )}
                    {alert.notifyPush && (
                      <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded">Push</span>
                    )}
                  </div>
                  <button
                    onClick={() => deleteAlert(alert.id)}
                    className="p-2 hover:bg-red-100 rounded-xl text-gray-400 hover:text-red-500 transition"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-10 text-center">
            <div className="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
            </div>
            <p className="text-gray-600 font-medium">No active alerts</p>
            <p className="text-gray-400 text-sm mt-1">Create an alert to get notified when prices change</p>
          </div>
        )}
      </div>

      {/* Triggered Alerts */}
      {triggeredAlerts.length > 0 && (
        <div className="bg-white border border-gray-100 rounded-2xl shadow-sm overflow-hidden">
          <div className="p-5 border-b border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900">Triggered ({triggeredAlerts.length})</h2>
          </div>
          <div className="divide-y divide-gray-100">
            {triggeredAlerts.map((alert) => (
              <div key={alert.id} className="p-5 flex justify-between items-center bg-gray-50">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-gray-400 rounded-xl flex items-center justify-center text-white font-bold">
                    ✓
                  </div>
                  <div>
                    <div className="font-bold text-gray-700">
                      {alert.symbol.replace('.NS', '').replace('.BO', '')}
                    </div>
                    <div className="text-sm text-gray-500 line-through">
                      {getConditionLabel(alert.condition, alert.targetPrice)}
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => deleteAlert(alert.id)}
                  className="text-gray-400 hover:text-gray-600 text-sm"
                >
                  Dismiss
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Create Alert Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-6 w-full max-w-lg mx-4 shadow-xl">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Create Price Alert</h3>

            {/* Stock Search */}
            {!selectedStock ? (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Select Stock</label>
                <div className="relative">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => handleSearch(e.target.value)}
                    placeholder="Search by symbol or name..."
                    className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-gray-900"
                  />
                  {searchLoading && (
                    <div className="absolute right-4 top-1/2 -translate-y-1/2">
                      <div className="w-5 h-5 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
                    </div>
                  )}
                </div>
                {searchResults.length > 0 && (
                  <div className="mt-2 border border-gray-200 rounded-xl overflow-hidden max-h-48 overflow-y-auto">
                    {searchResults.map((result) => (
                      <button
                        key={result.symbol}
                        onClick={() => selectStock(result)}
                        className="w-full px-4 py-3 text-left hover:bg-emerald-50 border-b border-gray-100 last:border-b-0"
                      >
                        <span className="font-semibold text-gray-900">
                          {result.symbol.replace('.NS', '')}
                        </span>
                        <span className="text-gray-500 text-sm ml-2">{result.name}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div>
                {/* Selected Stock */}
                <div className="bg-emerald-50 rounded-xl p-4 mb-4 flex justify-between items-center">
                  <div>
                    <div className="font-bold text-gray-900">
                      {selectedStock.symbol.replace('.NS', '').replace('.BO', '')}
                    </div>
                    <div className="text-sm text-gray-600">{selectedStock.name}</div>
                    <div className="text-emerald-700 font-semibold mt-1">
                      Current: {formatINR(selectedStock.price)}
                    </div>
                  </div>
                  <button
                    onClick={() => setSelectedStock(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    Change
                  </button>
                </div>

                {/* Alert Condition */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Alert When</label>
                  <select
                    value={alertForm.condition}
                    onChange={(e) => setAlertForm({ ...alertForm, condition: e.target.value as typeof alertForm.condition })}
                    className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-gray-900"
                  >
                    <option value="above">Price goes above</option>
                    <option value="below">Price falls below</option>
                    <option value="percent_up">Price increases by %</option>
                    <option value="percent_down">Price decreases by %</option>
                  </select>
                </div>

                {/* Target Price/Percentage */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {alertForm.condition.includes('percent') ? 'Percentage' : 'Target Price (₹)'}
                  </label>
                  <input
                    type="number"
                    value={alertForm.targetPrice}
                    onChange={(e) => setAlertForm({ ...alertForm, targetPrice: e.target.value })}
                    placeholder={alertForm.condition.includes('percent') ? 'e.g., 5' : 'e.g., 2500'}
                    className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-gray-900"
                  />
                </div>

                {/* Notification Options */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Notify via</label>
                  <div className="space-y-3">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={alertForm.notifyEmail}
                        onChange={(e) => setAlertForm({ ...alertForm, notifyEmail: e.target.checked })}
                        className="w-4 h-4 text-emerald-600 border-gray-300 rounded focus:ring-emerald-500"
                      />
                      <span className="ml-2 text-gray-700">Email</span>
                    </label>
                    {alertForm.notifyEmail && user?.email && (
                      <div className="ml-6 p-2 bg-gray-50 rounded-lg text-sm text-gray-600">
                        Notifications will be sent to: <span className="font-medium text-gray-900">{user.email}</span>
                      </div>
                    )}
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={alertForm.notifyPush}
                        onChange={(e) => setAlertForm({ ...alertForm, notifyPush: e.target.checked })}
                        className="w-4 h-4 text-emerald-600 border-gray-300 rounded focus:ring-emerald-500"
                      />
                      <span className="ml-2 text-gray-700">Push</span>
                    </label>
                  </div>
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => {
                  setShowCreateModal(false);
                  setSelectedStock(null);
                  setSearchQuery('');
                  setSearchResults([]);
                }}
                className="flex-1 px-4 py-2.5 border border-gray-200 text-gray-700 rounded-xl font-semibold hover:bg-gray-50 transition"
              >
                Cancel
              </button>
              {selectedStock && (
                <button
                  onClick={createAlert}
                  disabled={!alertForm.targetPrice}
                  className="flex-1 bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 text-white px-4 py-2.5 rounded-xl font-semibold transition disabled:opacity-50"
                >
                  Create Alert
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
