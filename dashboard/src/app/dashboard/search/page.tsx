'use client';

import { useState, useEffect } from 'react';
import { StockQuote, getAllNSEStocks, getNSESectors, NSEStock, Sector, getStockQuote } from '@/lib/api';
import { StockSearch, StockDetailPanel } from '@/components/stocks';

export default function SearchPage() {
  const [selectedStock, setSelectedStock] = useState<StockQuote | null>(null);
  const [recentSearches, setRecentSearches] = useState<StockQuote[]>([]);
  const [nseStocks, setNseStocks] = useState<{ nifty_50: NSEStock[], nifty_next_50: NSEStock[], total_count: number } | null>(null);
  const [sectors, setSectors] = useState<Sector[]>([]);
  const [activeTab, setActiveTab] = useState<'nifty50' | 'niftyNext50' | 'sectors'>('nifty50');
  const [loadingStock, setLoadingStock] = useState<string | null>(null);

  useEffect(() => {
    // Fetch NSE stocks list
    getAllNSEStocks()
      .then(setNseStocks)
      .catch(console.error);
    
    // Fetch sectors
    getNSESectors()
      .then(data => setSectors(data.sectors))
      .catch(console.error);
  }, []);

  const handleSelectStock = (stock: StockQuote) => {
    setSelectedStock(stock);
    setRecentSearches((prev) => {
      const filtered = prev.filter((s) => s.symbol !== stock.symbol);
      return [stock, ...filtered].slice(0, 10);
    });
  };

  const handleQuickSelect = async (symbol: string) => {
    setLoadingStock(symbol);
    try {
      const quote = await getStockQuote(symbol);
      handleSelectStock(quote);
    } catch (err) {
      console.error('Failed to fetch:', err);
    } finally {
      setLoadingStock(null);
    }
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
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Search NSE Stocks</h1>
        <p className="text-gray-500 mt-1">
          Search across {nseStocks?.total_count || '200+'} National Stock Exchange listed companies
        </p>
      </div>

      <div className="bg-white border border-gray-100 rounded-2xl p-5 shadow-sm">
        <StockSearch onSelectStock={handleSelectStock} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Recent Searches */}
          {recentSearches.length > 0 && (
            <div className="bg-white border border-gray-100 rounded-2xl shadow-sm overflow-hidden">
              <div className="p-5 border-b border-gray-100 flex justify-between items-center">
                <h2 className="text-lg font-semibold text-gray-900">Recent Searches</h2>
                <button
                  onClick={() => setRecentSearches([])}
                  className="text-sm text-gray-500 hover:text-gray-700"
                >
                  Clear
                </button>
              </div>
              <div className="divide-y divide-gray-100">
                {recentSearches.slice(0, 5).map((stock) => {
                  const changePercent = parseFloat(stock.change_percent);
                  const isPositive = changePercent >= 0;
                  const displaySymbol = stock.symbol.replace('.NS', '').replace('.BO', '');
                  return (
                    <button
                      key={stock.symbol}
                      onClick={() => setSelectedStock(stock)}
                      className="w-full p-4 text-left hover:bg-emerald-50 transition flex justify-between items-center"
                    >
                      <div className="flex items-center space-x-3">
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-white font-bold text-sm ${
                          isPositive ? 'bg-gradient-to-br from-emerald-500 to-green-600' : 'bg-gradient-to-br from-red-500 to-rose-600'
                        }`}>
                          {displaySymbol.substring(0, 2)}
                        </div>
                        <div>
                          <span className="font-semibold text-gray-900">{displaySymbol}</span>
                          <p className="text-sm text-gray-500 truncate max-w-[200px]">{stock.name}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="text-gray-900 font-bold">{formatINR(stock.price)}</span>
                        <p className={`text-sm font-semibold ${isPositive ? 'text-emerald-600' : 'text-red-600'}`}>
                          {isPositive ? '+' : ''}{changePercent.toFixed(2)}%
                        </p>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Browse NSE Stocks */}
          <div className="bg-white border border-gray-100 rounded-2xl shadow-sm overflow-hidden">
            <div className="p-5 border-b border-gray-100">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Browse NSE Stocks</h2>
              <div className="flex space-x-2">
                <button
                  onClick={() => setActiveTab('nifty50')}
                  className={`px-4 py-2 rounded-xl text-sm font-semibold transition ${
                    activeTab === 'nifty50'
                      ? 'bg-emerald-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  NIFTY 50
                </button>
                <button
                  onClick={() => setActiveTab('niftyNext50')}
                  className={`px-4 py-2 rounded-xl text-sm font-semibold transition ${
                    activeTab === 'niftyNext50'
                      ? 'bg-emerald-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  NIFTY Next 50
                </button>
                <button
                  onClick={() => setActiveTab('sectors')}
                  className={`px-4 py-2 rounded-xl text-sm font-semibold transition ${
                    activeTab === 'sectors'
                      ? 'bg-emerald-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  By Sector
                </button>
              </div>
            </div>
            <div className="p-5">
              {activeTab === 'nifty50' && (
                <div className="flex flex-wrap gap-2">
                  {nseStocks?.nifty_50.map((stock) => {
                    const displaySymbol = stock.symbol.replace('.NS', '');
                    const isLoading = loadingStock === stock.symbol;
                    return (
                      <button
                        key={stock.symbol}
                        onClick={() => handleQuickSelect(stock.symbol)}
                        disabled={isLoading}
                        title={stock.name}
                        className="bg-emerald-50 hover:bg-emerald-100 text-emerald-700 px-3 py-2 rounded-lg text-sm font-semibold transition border border-emerald-200 disabled:opacity-50"
                      >
                        {isLoading ? (
                          <span className="flex items-center">
                            <div className="w-3 h-3 border-2 border-emerald-600 border-t-transparent rounded-full animate-spin mr-1"></div>
                            {displaySymbol}
                          </span>
                        ) : (
                          displaySymbol
                        )}
                      </button>
                    );
                  })}
                </div>
              )}

              {activeTab === 'niftyNext50' && (
                <div className="flex flex-wrap gap-2">
                  {nseStocks?.nifty_next_50.map((stock) => {
                    const displaySymbol = stock.symbol.replace('.NS', '');
                    const isLoading = loadingStock === stock.symbol;
                    return (
                      <button
                        key={stock.symbol}
                        onClick={() => handleQuickSelect(stock.symbol)}
                        disabled={isLoading}
                        title={stock.name}
                        className="bg-blue-50 hover:bg-blue-100 text-blue-700 px-3 py-2 rounded-lg text-sm font-semibold transition border border-blue-200 disabled:opacity-50"
                      >
                        {isLoading ? (
                          <span className="flex items-center">
                            <div className="w-3 h-3 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mr-1"></div>
                            {displaySymbol}
                          </span>
                        ) : (
                          displaySymbol
                        )}
                      </button>
                    );
                  })}
                </div>
              )}

              {activeTab === 'sectors' && (
                <div className="space-y-4">
                  {sectors.map((sector) => (
                    <div key={sector.name}>
                      <h3 className="text-sm font-semibold text-gray-700 mb-2">{sector.name}</h3>
                      <div className="flex flex-wrap gap-2">
                        {sector.stocks.map((symbol) => {
                          const displaySymbol = symbol.replace('.NS', '');
                          const isLoading = loadingStock === symbol;
                          return (
                            <button
                              key={symbol}
                              onClick={() => handleQuickSelect(symbol)}
                              disabled={isLoading}
                              className="bg-gray-50 hover:bg-gray-100 text-gray-700 px-3 py-1.5 rounded-lg text-xs font-medium transition border border-gray-200 disabled:opacity-50"
                            >
                              {isLoading ? (
                                <span className="flex items-center">
                                  <div className="w-2 h-2 border-2 border-gray-600 border-t-transparent rounded-full animate-spin mr-1"></div>
                                  {displaySymbol}
                                </span>
                              ) : (
                                displaySymbol
                              )}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Stock Detail Panel */}
        <div className="lg:col-span-1">
          {selectedStock ? (
            <StockDetailPanel
              stock={selectedStock}
              onClose={() => setSelectedStock(null)}
            />
          ) : (
            <div className="bg-white border border-gray-100 rounded-2xl p-10 text-center shadow-sm sticky top-6">
              <div className="w-16 h-16 bg-emerald-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <p className="text-gray-900 font-semibold">Select a Stock</p>
              <p className="text-gray-500 text-sm mt-1">Search or click on any stock to view detailed information</p>
              <div className="mt-4 text-xs text-gray-400">
                {nseStocks && (
                  <p>Tracking {nseStocks.total_count} NSE stocks</p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
