'use client';

import { useState, useEffect, useCallback } from 'react';
import { getStockQuote, StockQuote, searchStocks, SearchResult } from '@/lib/api';
import { useWebSocket } from '@/hooks';

interface Watchlist {
  id: string;
  name: string;
  symbols: string[];
  createdAt: string;
}

export default function WatchlistPage() {
  const [watchlists, setWatchlists] = useState<Watchlist[]>([]);
  const [selectedWatchlist, setSelectedWatchlist] = useState<Watchlist | null>(null);
  const [stockData, setStockData] = useState<Record<string, StockQuote>>({});
  const [loading, setLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showAddStockModal, setShowAddStockModal] = useState(false);
  const [newWatchlistName, setNewWatchlistName] = useState('');
  const [newStockSymbol, setNewStockSymbol] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [realtimeEnabled, setRealtimeEnabled] = useState(true);
  
  // WebSocket for real-time updates
  const { isConnected, priceUpdates, subscribe, unsubscribe } = useWebSocket(
    realtimeEnabled ? { userId: 'watchlist-user' } : undefined
  );

  // Apply real-time price updates
  useEffect(() => {
    if (Object.keys(priceUpdates).length > 0) {
      setStockData((prev) => {
        const updated = { ...prev };
        for (const [symbol, price] of Object.entries(priceUpdates)) {
          if (updated[symbol]) {
            const oldClose = parseFloat(updated[symbol].previous_close);
            const change = price - oldClose;
            const changePercent = (change / oldClose) * 100;
            updated[symbol] = {
              ...updated[symbol],
              price: price.toFixed(2),
              change: change.toFixed(2),
              change_percent: changePercent.toFixed(2),
            };
          }
        }
        return updated;
      });
    }
  }, [priceUpdates]);

  // Subscribe to symbols when watchlist changes
  useEffect(() => {
    if (selectedWatchlist && realtimeEnabled) {
      selectedWatchlist.symbols.forEach((symbol) => subscribe(symbol));
      return () => {
        selectedWatchlist.symbols.forEach((symbol) => unsubscribe(symbol));
      };
    }
  }, [selectedWatchlist, realtimeEnabled, subscribe, unsubscribe]);

  useEffect(() => {
    const savedWatchlists = localStorage.getItem('watchlists');
    if (savedWatchlists) {
      const parsed = JSON.parse(savedWatchlists);
      setWatchlists(parsed);
      if (parsed.length > 0) {
        setSelectedWatchlist(parsed[0]);
      }
    } else {
      const defaultWatchlists: Watchlist[] = [
        {
          id: '1',
          name: 'Nifty 50 Picks',
          symbols: ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS'],
          createdAt: new Date().toISOString(),
        },
        {
          id: '2',
          name: 'Banking Stocks',
          symbols: ['HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'KOTAKBANK.NS', 'AXISBANK.NS'],
          createdAt: new Date().toISOString(),
        },
      ];
      localStorage.setItem('watchlists', JSON.stringify(defaultWatchlists));
      setWatchlists(defaultWatchlists);
      setSelectedWatchlist(defaultWatchlists[0]);
    }
  }, []);

  useEffect(() => {
    if (selectedWatchlist && selectedWatchlist.symbols.length > 0) {
      fetchStockData(selectedWatchlist.symbols);
    }
  }, [selectedWatchlist]);

  const fetchStockData = async (symbols: string[]) => {
    setLoading(true);
    const data: Record<string, StockQuote> = {};
    const failedSymbols: string[] = [];
    
    for (const symbol of symbols) {
      try {
        const quote = await getStockQuote(symbol);
        data[symbol] = quote;
      } catch (err) {
        console.warn(`Could not fetch data for ${symbol} - it may be an invalid symbol`);
        failedSymbols.push(symbol);
      }
    }
    
    // If some symbols failed, create placeholder data so UI can show them
    for (const symbol of failedSymbols) {
      data[symbol] = {
        symbol,
        name: `${symbol.replace('.NS', '').replace('.BO', '')} (Invalid Symbol)`,
        price: '0',
        change: '0',
        change_percent: '0',
        volume: 0,
        market_cap: null,
        high: '0',
        low: '0',
        open: '0',
        previous_close: '0',
        timestamp: new Date().toISOString(),
      };
    }
    
    setStockData(data);
    setLoading(false);
  };

  const saveWatchlists = (updated: Watchlist[]) => {
    localStorage.setItem('watchlists', JSON.stringify(updated));
    setWatchlists(updated);
  };

  const createWatchlist = () => {
    if (!newWatchlistName.trim()) return;
    const newWatchlist: Watchlist = {
      id: Date.now().toString(),
      name: newWatchlistName,
      symbols: [],
      createdAt: new Date().toISOString(),
    };
    const updated = [...watchlists, newWatchlist];
    saveWatchlists(updated);
    setSelectedWatchlist(newWatchlist);
    setNewWatchlistName('');
    setShowCreateModal(false);
  };

  const deleteWatchlist = (id: string) => {
    const updated = watchlists.filter((w) => w.id !== id);
    saveWatchlists(updated);
    if (selectedWatchlist?.id === id) {
      setSelectedWatchlist(updated[0] || null);
    }
  };

  const addStockToWatchlist = () => {
    if (!selectedWatchlist || !newStockSymbol.trim()) return;
    const symbol = newStockSymbol.toUpperCase().endsWith('.NS') || newStockSymbol.toUpperCase().endsWith('.BO')
      ? newStockSymbol.toUpperCase()
      : `${newStockSymbol.toUpperCase()}.NS`;
    
    if (selectedWatchlist.symbols.includes(symbol)) {
      alert('Stock already in watchlist');
      return;
    }
    
    const updated = watchlists.map((w) =>
      w.id === selectedWatchlist.id
        ? { ...w, symbols: [...w.symbols, symbol] }
        : w
    );
    saveWatchlists(updated);
    setSelectedWatchlist({ ...selectedWatchlist, symbols: [...selectedWatchlist.symbols, symbol] });
    setNewStockSymbol('');
    setShowAddStockModal(false);
    fetchStockData([symbol]);
  };

  const addStockFromSearch = (symbol: string) => {
    if (!selectedWatchlist) return;
    
    if (selectedWatchlist.symbols.includes(symbol)) {
      return; // Already added
    }
    
    const updated = watchlists.map((w) =>
      w.id === selectedWatchlist.id
        ? { ...w, symbols: [...w.symbols, symbol] }
        : w
    );
    saveWatchlists(updated);
    setSelectedWatchlist({ ...selectedWatchlist, symbols: [...selectedWatchlist.symbols, symbol] });
    setSearchResults(searchResults.map(r => r)); // Force re-render to show "Added" state
    fetchStockData([symbol]);
  };

  const removeStockFromWatchlist = (symbol: string) => {
    if (!selectedWatchlist) return;
    const updated = watchlists.map((w) =>
      w.id === selectedWatchlist.id
        ? { ...w, symbols: w.symbols.filter((s) => s !== symbol) }
        : w
    );
    saveWatchlists(updated);
    setSelectedWatchlist({ ...selectedWatchlist, symbols: selectedWatchlist.symbols.filter((s) => s !== symbol) });
  };

  const formatINR = (price: string) => {
    const num = parseFloat(price);
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
    }).format(num);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">My Watchlists</h1>
          <p className="text-gray-500 mt-1">Track your favorite NSE & BSE stocks</p>
        </div>
        <div className="flex items-center space-x-4">
          {/* Real-time indicator */}
          <div className="flex items-center space-x-2 bg-white border border-gray-200 rounded-xl px-4 py-2">
            <button
              onClick={() => setRealtimeEnabled(!realtimeEnabled)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                realtimeEnabled ? 'bg-emerald-500' : 'bg-gray-300'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  realtimeEnabled ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
            <span className="text-sm font-medium text-gray-700">Live</span>
            {realtimeEnabled && (
              <span className={`flex h-2 w-2 ${isConnected ? 'bg-emerald-500' : 'bg-yellow-500'} rounded-full animate-pulse`} />
            )}
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 text-white px-5 py-2.5 rounded-xl font-semibold transition shadow-sm flex items-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            <span>New Watchlist</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Watchlist Sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-white border border-gray-100 rounded-2xl shadow-sm overflow-hidden">
            <div className="p-4 border-b border-gray-100">
              <h2 className="font-semibold text-gray-900">Watchlists</h2>
            </div>
            <div className="divide-y divide-gray-100">
              {watchlists.map((watchlist) => (
                <div
                  key={watchlist.id}
                  onClick={() => setSelectedWatchlist(watchlist)}
                  className={`w-full p-4 text-left transition flex justify-between items-center cursor-pointer ${
                    selectedWatchlist?.id === watchlist.id
                      ? 'bg-emerald-50 border-l-4 border-emerald-500'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <div>
                    <span className={`font-semibold ${selectedWatchlist?.id === watchlist.id ? 'text-emerald-700' : 'text-gray-900'}`}>
                      {watchlist.name}
                    </span>
                    <p className="text-sm text-gray-500">{watchlist.symbols.length} stocks</p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      if (confirm('Delete this watchlist?')) {
                        deleteWatchlist(watchlist.id);
                      }
                    }}
                    className="p-1.5 hover:bg-red-100 rounded-lg text-gray-400 hover:text-red-500 transition"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              ))}
              {watchlists.length === 0 && (
                <div className="p-6 text-center text-gray-500">
                  No watchlists yet
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Stock List */}
        <div className="lg:col-span-3">
          {selectedWatchlist ? (
            <div className="bg-white border border-gray-100 rounded-2xl shadow-sm overflow-hidden">
              <div className="p-5 border-b border-gray-100 flex justify-between items-center">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">{selectedWatchlist.name}</h2>
                  <p className="text-sm text-gray-500">{selectedWatchlist.symbols.length} stocks</p>
                </div>
                <button
                  onClick={() => setShowAddStockModal(true)}
                  className="bg-emerald-50 hover:bg-emerald-100 text-emerald-700 px-4 py-2 rounded-xl font-semibold transition border border-emerald-200 flex items-center space-x-2"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  <span>Add Stock</span>
                </button>
              </div>

              {loading ? (
                <div className="p-10 text-center">
                  <div className="animate-spin rounded-full h-10 w-10 border-4 border-emerald-200 border-t-emerald-600 mx-auto"></div>
                  <p className="text-gray-500 mt-4">Loading stocks...</p>
                </div>
              ) : selectedWatchlist.symbols.length > 0 ? (
                <div className="divide-y divide-gray-100">
                  {selectedWatchlist.symbols.map((symbol) => {
                    const stock = stockData[symbol];
                    const displaySymbol = symbol.replace('.NS', '').replace('.BO', '');
                    if (!stock) {
                      return (
                        <div key={symbol} className="p-4 flex justify-between items-center">
                          <span className="text-gray-900 font-semibold">{displaySymbol}</span>
                          <span className="text-gray-400 text-sm">Loading...</span>
                        </div>
                      );
                    }
                    const changePercent = parseFloat(stock.change_percent);
                    const isPositive = changePercent >= 0;
                    const isInvalid = stock.name.includes('Invalid Symbol') || parseFloat(stock.price) === 0;
                    
                    return (
                      <div key={symbol} className={`p-4 flex justify-between items-center hover:bg-gray-50 transition ${isInvalid ? 'bg-amber-50' : ''}`}>
                        <div className="flex items-center space-x-3">
                          <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-white font-bold ${
                            isInvalid ? 'bg-gradient-to-br from-amber-400 to-orange-500' : 
                            isPositive ? 'bg-gradient-to-br from-emerald-500 to-green-600' : 'bg-gradient-to-br from-red-500 to-rose-600'
                          }`}>
                            {isInvalid ? '?' : displaySymbol.substring(0, 2)}
                          </div>
                          <div>
                            <span className="font-bold text-gray-900">{displaySymbol}</span>
                            {isInvalid ? (
                              <p className="text-sm text-amber-600">Invalid symbol - please remove</p>
                            ) : (
                              <p className="text-sm text-gray-500 truncate max-w-[200px]">{stock.name}</p>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center space-x-6">
                          {!isInvalid && (
                            <div className="text-right">
                              <span className="text-lg font-bold text-gray-900">{formatINR(stock.price)}</span>
                              <p className={`text-sm font-semibold ${isPositive ? 'text-emerald-600' : 'text-red-600'}`}>
                                {isPositive ? '▲' : '▼'} {isPositive ? '+' : ''}{changePercent.toFixed(2)}%
                              </p>
                            </div>
                          )}
                          <button
                            onClick={() => removeStockFromWatchlist(symbol)}
                            className="p-2 hover:bg-red-100 rounded-xl text-gray-400 hover:text-red-500 transition"
                          >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="p-10 text-center">
                  <div className="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                  </div>
                  <p className="text-gray-600 font-medium">No stocks in this watchlist</p>
                  <p className="text-gray-400 text-sm mt-1">Click "Add Stock" to get started</p>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-white border border-gray-100 rounded-2xl p-10 text-center shadow-sm">
              <div className="w-16 h-16 bg-emerald-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <p className="text-gray-900 font-semibold">No Watchlist Selected</p>
              <p className="text-gray-500 text-sm mt-1">Select or create a watchlist to view stocks</p>
            </div>
          )}
        </div>
      </div>

      {/* Create Watchlist Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-6 w-full max-w-md mx-4 shadow-xl">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Create Watchlist</h3>
            <input
              type="text"
              value={newWatchlistName}
              onChange={(e) => setNewWatchlistName(e.target.value)}
              placeholder="Watchlist name..."
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 mb-4 text-gray-900"
            />
            <div className="flex space-x-3">
              <button
                onClick={() => setShowCreateModal(false)}
                className="flex-1 px-4 py-2.5 border border-gray-200 text-gray-700 rounded-xl font-semibold hover:bg-gray-50 transition"
              >
                Cancel
              </button>
              <button
                onClick={createWatchlist}
                className="flex-1 bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 text-white px-4 py-2.5 rounded-xl font-semibold transition"
              >
                Create
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Stock Modal with Search */}
      {showAddStockModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-6 w-full max-w-lg mx-4 shadow-xl">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Add Stock to {selectedWatchlist?.name}</h3>
            <div className="relative">
              <input
                type="text"
                value={newStockSymbol}
                onChange={async (e) => {
                  const query = e.target.value;
                  setNewStockSymbol(query);
                  if (query.length >= 1) {
                    setSearchLoading(true);
                    try {
                      const results = await searchStocks(query, false, 10);
                      setSearchResults(results);
                    } catch {
                      setSearchResults([]);
                    } finally {
                      setSearchLoading(false);
                    }
                  } else {
                    setSearchResults([]);
                  }
                }}
                placeholder="Search by symbol or company name..."
                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-gray-900"
              />
              {searchLoading && (
                <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
                  <div className="w-5 h-5 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
                </div>
              )}
            </div>
            
            {/* Search Results */}
            {searchResults.length > 0 && (
              <div className="mt-2 max-h-64 overflow-y-auto border border-gray-200 rounded-xl">
                {searchResults.map((result) => {
                  const displaySymbol = result.symbol.replace('.NS', '').replace('.BO', '');
                  const isAlreadyAdded = selectedWatchlist?.symbols.includes(result.symbol);
                  return (
                    <button
                      key={result.symbol}
                      onClick={() => {
                        if (!isAlreadyAdded) {
                          addStockFromSearch(result.symbol);
                        }
                      }}
                      disabled={isAlreadyAdded}
                      className={`w-full px-4 py-3 text-left border-b border-gray-100 last:border-b-0 transition ${
                        isAlreadyAdded 
                          ? 'bg-gray-50 cursor-not-allowed' 
                          : 'hover:bg-emerald-50'
                      }`}
                    >
                      <div className="flex justify-between items-center">
                        <div>
                          <span className="font-semibold text-gray-900">{displaySymbol}</span>
                          <span className="text-gray-500 text-sm ml-2">{result.name}</span>
                        </div>
                        {isAlreadyAdded ? (
                          <span className="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded">Added</span>
                        ) : (
                          <span className="text-emerald-600 text-sm">+ Add</span>
                        )}
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
            
            {newStockSymbol.length > 0 && searchResults.length === 0 && !searchLoading && (
              <div className="mt-2 p-4 bg-gray-50 rounded-xl text-center text-gray-500 text-sm">
                No stocks found for &quot;{newStockSymbol}&quot;
              </div>
            )}
            
            <div className="flex space-x-3 mt-4">
              <button
                onClick={() => {
                  setShowAddStockModal(false);
                  setNewStockSymbol('');
                  setSearchResults([]);
                }}
                className="flex-1 px-4 py-2.5 border border-gray-200 text-gray-700 rounded-xl font-semibold hover:bg-gray-50 transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
