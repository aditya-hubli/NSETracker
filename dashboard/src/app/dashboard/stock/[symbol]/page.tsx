'use client';

import { useState, useEffect, use } from 'react';
import { getStockQuote, getStockHistory, StockQuote } from '@/lib/api';
import { StockChart } from '@/components/charts';
import { useWebSocket } from '@/hooks';
import Link from 'next/link';

export default function StockPage({ params }: { params: Promise<{ symbol: string }> }) {
  const { symbol } = use(params);
  const decodedSymbol = decodeURIComponent(symbol);
  
  const [stock, setStock] = useState<StockQuote | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [chartType, setChartType] = useState<'candlestick' | 'line' | 'area'>('candlestick');
  const [interval, setInterval] = useState<'1d' | '1h' | '15m' | '5m' | '1m'>('1d');
  const [realtimeEnabled, setRealtimeEnabled] = useState(true);

  // WebSocket for real-time updates
  const { isConnected, priceUpdates, subscribe, unsubscribe } = useWebSocket(
    realtimeEnabled ? { userId: 'stock-detail-user' } : undefined
  );

  useEffect(() => {
    const fetchStock = async () => {
      try {
        setLoading(true);
        const data = await getStockQuote(decodedSymbol);
        setStock(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load stock data');
      } finally {
        setLoading(false);
      }
    };
    
    fetchStock();
    
    if (realtimeEnabled) {
      subscribe(decodedSymbol);
    }
    
    return () => {
      if (realtimeEnabled) {
        unsubscribe(decodedSymbol);
      }
    };
  }, [decodedSymbol, realtimeEnabled, subscribe, unsubscribe]);

  // Apply real-time price updates
  useEffect(() => {
    const newPrice = priceUpdates[decodedSymbol];
    if (newPrice && stock) {
      const oldClose = parseFloat(stock.previous_close);
      const change = newPrice - oldClose;
      const changePercent = (change / oldClose) * 100;
      
      setStock({
        ...stock,
        price: newPrice.toFixed(2),
        change: change.toFixed(2),
        change_percent: changePercent.toFixed(2),
      });
    }
  }, [priceUpdates, decodedSymbol]);

  const formatINR = (price: string | number) => {
    const num = typeof price === 'string' ? parseFloat(price) : price;
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
    }).format(num);
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-IN').format(num);
  };

  const formatMarketCap = (cap: string | null) => {
    if (!cap) return 'N/A';
    const num = parseFloat(cap);
    if (num >= 1e12) return `₹${(num / 1e12).toFixed(2)} L Cr`;
    if (num >= 1e7) return `₹${(num / 1e7).toFixed(2)} Cr`;
    if (num >= 1e5) return `₹${(num / 1e5).toFixed(2)} L`;
    return `₹${formatNumber(num)}`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading stock data...</p>
        </div>
      </div>
    );
  }

  if (error || !stock) {
    return (
      <div className="text-center py-20">
        <div className="text-red-500 text-xl mb-4">Error loading stock</div>
        <p className="text-gray-500">{error || 'Stock not found'}</p>
        <Link href="/dashboard" className="text-emerald-600 hover:text-emerald-700 mt-4 inline-block">
          ← Back to Dashboard
        </Link>
      </div>
    );
  }

  const change = parseFloat(stock.change);
  const changePercent = parseFloat(stock.change_percent);
  const isPositive = change >= 0;
  const displaySymbol = stock.symbol.replace('.NS', '').replace('.BO', '');
  const exchange = stock.symbol.includes('.NS') ? 'NSE' : stock.symbol.includes('.BO') ? 'BSE' : '';

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <div className="flex items-center space-x-2 text-sm">
        <Link href="/dashboard" className="text-gray-500 hover:text-emerald-600">Dashboard</Link>
        <span className="text-gray-400">/</span>
        <span className="text-gray-900 font-medium">{displaySymbol}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
        <div className="flex items-center space-x-4">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-500 to-green-600 flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-emerald-500/30">
            {displaySymbol.substring(0, 2)}
          </div>
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-3xl font-bold text-gray-900">{displaySymbol}</h1>
              {exchange && (
                <span className="px-3 py-1 rounded-full bg-emerald-100 text-emerald-700 text-sm font-medium">{exchange}</span>
              )}
            </div>
            <p className="text-gray-500">{stock.name}</p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          {/* Real-time Toggle */}
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

          <button className="bg-white border border-gray-200 hover:bg-gray-50 text-gray-700 px-4 py-2.5 rounded-xl font-medium transition flex items-center space-x-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
            </svg>
            <span>Add to Watchlist</span>
          </button>

          <button className="bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 text-white px-4 py-2.5 rounded-xl font-medium transition shadow-sm flex items-center space-x-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <span>Set Alert</span>
          </button>
        </div>
      </div>

      {/* Price Card */}
      <div className="bg-white border border-gray-100 rounded-2xl shadow-sm p-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <p className="text-4xl font-bold text-gray-900">{formatINR(stock.price)}</p>
            <div className="flex items-center mt-2 space-x-3">
              <div className={`flex items-center px-3 py-1.5 rounded-lg ${isPositive ? 'bg-emerald-100' : 'bg-red-100'}`}>
                <svg className={`w-4 h-4 ${isPositive ? 'text-emerald-600' : 'text-red-600'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={isPositive ? "M5 10l7-7m0 0l7 7m-7-7v18" : "M19 14l-7 7m0 0l-7-7m7 7V3"} />
                </svg>
                <span className={`text-sm font-bold ml-1 ${isPositive ? 'text-emerald-600' : 'text-red-600'}`}>
                  {isPositive ? '+' : ''}{formatINR(change)} ({isPositive ? '+' : ''}{changePercent.toFixed(2)}%)
                </span>
              </div>
              <span className="text-sm text-gray-500">Today</span>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center bg-gray-50 rounded-xl p-3">
              <span className="text-xs text-gray-500 block">Open</span>
              <span className="font-semibold text-gray-900">{formatINR(stock.open)}</span>
            </div>
            <div className="text-center bg-emerald-50 rounded-xl p-3">
              <span className="text-xs text-emerald-600 block">High</span>
              <span className="font-semibold text-emerald-700">{formatINR(stock.high)}</span>
            </div>
            <div className="text-center bg-red-50 rounded-xl p-3">
              <span className="text-xs text-red-600 block">Low</span>
              <span className="font-semibold text-red-700">{formatINR(stock.low)}</span>
            </div>
            <div className="text-center bg-gray-50 rounded-xl p-3">
              <span className="text-xs text-gray-500 block">Prev Close</span>
              <span className="font-semibold text-gray-900">{formatINR(stock.previous_close)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-white border border-gray-100 rounded-2xl shadow-sm overflow-hidden">
        <div className="p-5 border-b border-gray-100 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <h2 className="text-lg font-bold text-gray-900">Price Chart</h2>
          
          <div className="flex items-center space-x-4">
            {/* Chart Type Selector */}
            <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
              {[
                { key: 'candlestick', icon: 'C', label: 'Candlestick' },
                { key: 'line', icon: 'L', label: 'Line' },
                { key: 'area', icon: 'A', label: 'Area' },
              ].map((type) => (
                <button
                  key={type.key}
                  onClick={() => setChartType(type.key as typeof chartType)}
                  className={`px-3 py-1.5 rounded text-sm font-medium transition ${
                    chartType === type.key
                      ? 'bg-white text-gray-900 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                  title={type.label}
                >
                  {type.icon}
                </button>
              ))}
            </div>

            {/* Interval Selector */}
            <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
              {[
                { key: '1m', label: '1M' },
                { key: '5m', label: '5M' },
                { key: '15m', label: '15M' },
                { key: '1h', label: '1H' },
                { key: '1d', label: '1D' },
              ].map((int) => (
                <button
                  key={int.key}
                  onClick={() => setInterval(int.key as typeof interval)}
                  className={`px-3 py-1.5 rounded text-xs font-medium transition ${
                    interval === int.key
                      ? 'bg-emerald-500 text-white'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  {int.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="p-5">
          <StockChart
            symbol={stock.symbol}
            chartType={chartType}
            interval={interval}
            height={500}
            showVolume={true}
          />
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white border border-gray-100 rounded-2xl p-5 shadow-sm">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center">
              <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <div>
              <span className="text-xs text-gray-500 block">Volume</span>
              <span className="font-bold text-gray-900">{formatNumber(stock.volume)}</span>
            </div>
          </div>
        </div>

        <div className="bg-white border border-gray-100 rounded-2xl p-5 shadow-sm">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-purple-100 flex items-center justify-center">
              <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <span className="text-xs text-gray-500 block">Market Cap</span>
              <span className="font-bold text-gray-900">{formatMarketCap(stock.market_cap)}</span>
            </div>
          </div>
        </div>

        <div className="bg-white border border-gray-100 rounded-2xl p-5 shadow-sm">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-100 flex items-center justify-center">
              <svg className="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <span className="text-xs text-gray-500 block">52W High</span>
              <span className="font-bold text-emerald-600">Coming Soon</span>
            </div>
          </div>
        </div>

        <div className="bg-white border border-gray-100 rounded-2xl p-5 shadow-sm">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-red-100 flex items-center justify-center">
              <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <span className="text-xs text-gray-500 block">52W Low</span>
              <span className="font-bold text-red-600">Coming Soon</span>
            </div>
          </div>
        </div>
      </div>

      {/* About Section */}
      <div className="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm">
        <h2 className="text-lg font-bold text-gray-900 mb-4">About {displaySymbol}</h2>
        <p className="text-gray-600 leading-relaxed">
          {stock.name} ({displaySymbol}) is listed on the {exchange === 'NSE' ? 'National Stock Exchange (NSE)' : exchange === 'BSE' ? 'Bombay Stock Exchange (BSE)' : 'Indian stock exchange'}.
          View real-time price updates, historical charts, and set price alerts to track your investment.
        </p>
      </div>
    </div>
  );
}
