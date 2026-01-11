'use client';

import { useState, useEffect, useCallback } from 'react';
import { StockQuote, MarketSummary, TopMovers, getMarketSummary, getTopMovers } from '@/lib/api';
import { StockCard, StockDetailPanel } from '@/components/stocks';

export default function DashboardPage() {
  const [marketSummary, setMarketSummary] = useState<MarketSummary | null>(null);
  const [topMovers, setTopMovers] = useState<TopMovers | null>(null);
  const [selectedStock, setSelectedStock] = useState<StockQuote | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'gainers' | 'losers' | 'active'>('overview');
  const [currentTime, setCurrentTime] = useState(new Date());

  // Update time every second
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const fetchData = useCallback(async () => {
    try {
      setError(null);
      const [summary, movers] = await Promise.all([
        getMarketSummary().catch(() => null),
        getTopMovers().catch(() => null),
      ]);
      if (summary) setMarketSummary(summary);
      if (movers) setTopMovers(movers);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const formatINR = (price: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
    }).format(price);
  };

  const marketStatusColors = {
    open: 'bg-emerald-100 text-emerald-700 border-emerald-200',
    closed: 'bg-red-100 text-red-700 border-red-200',
    pre_market: 'bg-amber-100 text-amber-700 border-amber-200',
    after_hours: 'bg-purple-100 text-purple-700 border-purple-200',
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading market data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Market Overview</h1>
          <p className="text-gray-500 mt-1">NSE & BSE Real-time Market Data</p>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-gray-900">
            {currentTime.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
          </p>
          <p className="text-sm text-gray-500">
            {currentTime.toLocaleDateString('en-IN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
          </p>
          <div className="flex items-center justify-end space-x-3 mt-2">
            {marketSummary && (
              <span className={`px-3 py-1.5 rounded-full text-sm font-medium border ${marketStatusColors[marketSummary.market_status]}`}>
                <span className="w-2 h-2 inline-block rounded-full bg-current mr-2 animate-pulse"></span>
                Market {marketSummary.market_status.replace('_', ' ')}
              </span>
            )}
            <button
              onClick={fetchData}
              className="bg-white hover:bg-gray-50 text-gray-700 px-4 py-2 rounded-lg transition flex items-center space-x-2 border border-gray-200 shadow-sm"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <span>Refresh</span>
            </button>
          </div>
        </div>
      </div>

      {/* Market Indices */}
      {marketSummary && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {marketSummary.indices.map((index) => {
            const change = parseFloat(index.change);
            const changePercent = parseFloat(index.change_percent);
            const isPositive = change >= 0;
            return (
              <div
                key={index.symbol}
                onClick={() => setSelectedStock(index)}
                className="bg-white rounded-2xl p-5 cursor-pointer hover:shadow-lg transition-all border border-gray-100 group"
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm font-medium text-gray-500">{index.name}</span>
                  <span className={`text-xs px-2 py-1 rounded-full ${isPositive ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'}`}>
                    {index.symbol.includes('NSEI') ? 'NSE' : index.symbol.includes('BSE') ? 'BSE' : 'Index'}
                  </span>
                </div>
                <p className="text-2xl font-bold text-gray-900 group-hover:text-emerald-600 transition">
                  {formatINR(parseFloat(index.price))}
                </p>
                <div className="flex items-center mt-2">
                  <svg className={`w-4 h-4 ${isPositive ? 'text-emerald-500' : 'text-red-500'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={isPositive ? "M5 10l7-7m0 0l7 7m-7-7v18" : "M19 14l-7 7m0 0l-7-7m7 7V3"} />
                  </svg>
                  <span className={`text-sm font-semibold ml-1 ${isPositive ? 'text-emerald-600' : 'text-red-600'}`}>
                    {isPositive ? '+' : ''}{change.toFixed(2)} ({isPositive ? '+' : ''}{changePercent.toFixed(2)}%)
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-xl w-fit">
        {[
          { key: 'overview', label: 'Overview' },
          { key: 'gainers', label: 'Top Gainers' },
          { key: 'losers', label: 'Top Losers' },
          { key: 'active', label: 'Most Active' },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as typeof activeTab)}
            className={`px-5 py-2.5 rounded-lg text-sm font-medium transition-all ${
              activeTab === tab.key
                ? 'bg-white text-emerald-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-4">
          {activeTab === 'overview' && (
            <>
              <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
                <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                  <span className="w-2 h-2 bg-emerald-500 rounded-full mr-2"></span>
                  Top NIFTY 50 Stocks
                </h2>
                <div className="space-y-3">
                  {topMovers?.gainers.slice(0, 5).map((stock) => (
                    <StockCard key={stock.symbol} stock={stock} onClick={() => setSelectedStock(stock)} compact />
                  ))}
                </div>
              </div>
            </>
          )}

          {activeTab === 'gainers' && topMovers && (
            <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
              <h2 className="text-lg font-bold text-gray-900 mb-4">Top Gainers</h2>
              <div className="space-y-3">
                {topMovers.gainers.map((stock) => (
                  <StockCard key={stock.symbol} stock={stock} onClick={() => setSelectedStock(stock)} />
                ))}
              </div>
            </div>
          )}

          {activeTab === 'losers' && topMovers && (
            <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
              <h2 className="text-lg font-bold text-gray-900 mb-4">Top Losers</h2>
              <div className="space-y-3">
                {topMovers.losers.map((stock) => (
                  <StockCard key={stock.symbol} stock={stock} onClick={() => setSelectedStock(stock)} />
                ))}
              </div>
            </div>
          )}

          {activeTab === 'active' && topMovers && (
            <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
              <h2 className="text-lg font-bold text-gray-900 mb-4">Most Active</h2>
              <div className="space-y-3">
                {topMovers.most_active.map((stock) => (
                  <StockCard key={stock.symbol} stock={stock} onClick={() => setSelectedStock(stock)} />
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar - Stock Detail or Market Info */}
        <div className="space-y-4">
          {selectedStock ? (
            <StockDetailPanel stock={selectedStock} onClose={() => setSelectedStock(null)} />
          ) : (
            <>
              {/* Market Breadth */}
              <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Market Breadth</h3>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-emerald-600 font-medium">Advances: 1,245</span>
                      <span className="text-red-600 font-medium">Declines: 856</span>
                    </div>
                    <div className="h-3 bg-gray-100 rounded-full overflow-hidden flex">
                      <div className="bg-emerald-500 h-full" style={{ width: '59%' }}></div>
                      <div className="bg-red-500 h-full" style={{ width: '41%' }}></div>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-100">
                    <div className="text-center">
                      <p className="text-2xl font-bold text-emerald-600">59%</p>
                      <p className="text-xs text-gray-500">Bullish</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-red-600">41%</p>
                      <p className="text-xs text-gray-500">Bearish</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Sector Performance */}
              <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Sector Performance</h3>
                <div className="space-y-3">
                  {[
                    { name: 'IT', change: 2.34, isPositive: true },
                    { name: 'Banking', change: 1.56, isPositive: true },
                    { name: 'Pharma', change: -0.82, isPositive: false },
                    { name: 'Auto', change: 1.12, isPositive: true },
                    { name: 'FMCG', change: -0.45, isPositive: false },
                  ].map((sector) => (
                    <div key={sector.name} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                      <span className="font-medium text-gray-700">{sector.name}</span>
                      <span className={`font-semibold ${sector.isPositive ? 'text-emerald-600' : 'text-red-600'}`}>
                        {sector.isPositive ? '+' : ''}{sector.change}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl">
          {error}
        </div>
      )}
    </div>
  );
}
