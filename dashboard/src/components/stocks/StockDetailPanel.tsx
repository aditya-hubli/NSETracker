'use client';

import { StockQuote, StockHistory } from '@/lib/api';
import { useEffect, useState } from 'react';
import { getStockHistory } from '@/lib/api';
import Link from 'next/link';

interface StockDetailPanelProps {
  stock: StockQuote;
  onClose: () => void;
  onAddToWatchlist?: (symbol: string) => void;
}

function MiniChart({ data, color }: { data: number[]; color: string }) {
  if (data.length < 2) return <div className="h-24 flex items-center justify-center text-gray-400">No data available</div>;

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const height = 100;
  const width = 300;

  const points = data.map((val, i) => {
    const x = (i / (data.length - 1)) * width;
    const y = height - ((val - min) / range) * height;
    return `${x},${y}`;
  }).join(' ');

  return (
    <svg width={width} height={height} className="w-full">
      <defs>
        <linearGradient id={`gradient-${color.replace('#', '')}`} x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor={color} stopOpacity="0.2" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <polygon
        points={`0,${height} ${points} ${width},${height}`}
        fill={`url(#gradient-${color.replace('#', '')})`}
      />
      <polyline points={points} fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export default function StockDetailPanel({ stock, onClose, onAddToWatchlist }: StockDetailPanelProps) {
  const [history, setHistory] = useState<{ data: StockHistory | null; symbol: string } | null>(null);
  const [period, setPeriod] = useState<'1w' | '1mo' | '3mo'>('1mo');

  const change = parseFloat(stock.change);
  const changePercent = parseFloat(stock.change_percent);
  const isPositive = change >= 0;

  // Remove .NS or .BO suffix for display
  const displaySymbol = stock.symbol.replace('.NS', '').replace('.BO', '');
  const exchange = stock.symbol.includes('.NS') ? 'NSE' : stock.symbol.includes('.BO') ? 'BSE' : 'Stock';

  useEffect(() => {
    let isMounted = true;
    
    const periodMap: Record<string, string> = {
      '1w': '5d',
      '1mo': '1mo',
      '3mo': '3mo'
    };
    
    getStockHistory(stock.symbol, periodMap[period], '1d')
      .then((data) => {
        if (isMounted) {
          setHistory({ data, symbol: stock.symbol });
        }
      })
      .catch(() => {
        if (isMounted) {
          setHistory({ data: null, symbol: stock.symbol });
        }
      });
    
    return () => { isMounted = false; };
  }, [stock.symbol, period]);

  const loading = !history || history.symbol !== stock.symbol;
  const historyData = history?.symbol === stock.symbol ? history.data : null;

  const formatINR = (price: string | number): string => {
    const num = typeof price === 'string' ? parseFloat(price) : price;
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
    }).format(num);
  };

  const formatNumber = (num: number): string => {
    return new Intl.NumberFormat('en-IN').format(num);
  };

  const formatMarketCap = (cap: string | null): string => {
    if (!cap) return 'N/A';
    const num = parseFloat(cap);
    if (num >= 1e12) return `₹${(num / 1e12).toFixed(2)} L Cr`;
    if (num >= 1e7) return `₹${(num / 1e7).toFixed(2)} Cr`;
    if (num >= 1e5) return `₹${(num / 1e5).toFixed(2)} L`;
    return `₹${formatNumber(num)}`;
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-emerald-500 to-green-600 p-5 text-white">
        <div className="flex justify-between items-start">
          <div className="flex items-center space-x-4">
            <div className="w-14 h-14 rounded-xl bg-white/20 backdrop-blur flex items-center justify-center text-white font-bold text-lg">
              {displaySymbol.substring(0, 2)}
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-2xl font-bold">{displaySymbol}</h2>
                <span className="px-2 py-0.5 rounded-full bg-white/20 text-xs font-medium">{exchange}</span>
              </div>
              <p className="text-white/80 text-sm">{stock.name}</p>
            </div>
          </div>
          <button 
            onClick={onClose} 
            className="p-2 rounded-lg hover:bg-white/20 transition"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      {/* Price Section */}
      <div className="p-5 border-b border-gray-100">
        <div className="flex items-baseline space-x-3">
          <p className="text-3xl font-bold text-gray-900">{formatINR(stock.price)}</p>
          <div className={`flex items-center px-2 py-1 rounded-lg ${isPositive ? 'bg-emerald-100' : 'bg-red-100'}`}>
            <svg className={`w-4 h-4 ${isPositive ? 'text-emerald-600' : 'text-red-600'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={isPositive ? "M5 10l7-7m0 0l7 7m-7-7v18" : "M19 14l-7 7m0 0l-7-7m7 7V3"} />
            </svg>
            <span className={`text-sm font-bold ml-1 ${isPositive ? 'text-emerald-600' : 'text-red-600'}`}>
              {isPositive ? '+' : ''}{changePercent.toFixed(2)}%
            </span>
          </div>
        </div>
        <p className={`text-sm mt-1 ${isPositive ? 'text-emerald-600' : 'text-red-600'}`}>
          {isPositive ? '+' : ''}{formatINR(change)} today
        </p>
      </div>

      {/* Chart Section */}
      <div className="p-5 border-b border-gray-100">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-sm font-semibold text-gray-700">Price History</h3>
          <div className="flex items-center space-x-2">
            <div className="flex space-x-1">
              {(['1w', '1mo', '3mo'] as const).map((p) => (
                <button
                  key={p}
                  onClick={() => setPeriod(p)}
                  className={`px-3 py-1 rounded-lg text-xs font-medium transition ${
                    period === p 
                      ? 'bg-emerald-500 text-white' 
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {p === '1w' ? '1W' : p === '1mo' ? '1M' : '3M'}
                </button>
              ))}
            </div>
            <Link
              href={`/dashboard/stock/${encodeURIComponent(stock.symbol)}`}
              className="px-3 py-1 rounded-lg text-xs font-medium bg-gray-100 text-gray-600 hover:bg-gray-200 transition flex items-center space-x-1"
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
              <span>Full Chart</span>
            </Link>
          </div>
        </div>
        {loading ? (
          <div className="h-24 flex items-center justify-center">
            <div className="w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : historyData && historyData.data.length > 0 ? (
          <MiniChart
            data={historyData.data.map(d => parseFloat(d.close))}
            color={isPositive ? '#059669' : '#DC2626'}
          />
        ) : (
          <div className="h-24 flex items-center justify-center text-gray-400">No chart data available</div>
        )}
      </div>

      {/* Stats Grid */}
      <div className="p-5 grid grid-cols-2 gap-4">
        <div className="bg-gray-50 rounded-xl p-3">
          <span className="text-xs text-gray-500">Open</span>
          <p className="text-gray-900 font-semibold">{formatINR(stock.open)}</p>
        </div>
        <div className="bg-gray-50 rounded-xl p-3">
          <span className="text-xs text-gray-500">Prev Close</span>
          <p className="text-gray-900 font-semibold">{formatINR(stock.previous_close)}</p>
        </div>
        <div className="bg-emerald-50 rounded-xl p-3">
          <span className="text-xs text-emerald-600">Day High</span>
          <p className="text-emerald-700 font-semibold">{formatINR(stock.high)}</p>
        </div>
        <div className="bg-red-50 rounded-xl p-3">
          <span className="text-xs text-red-600">Day Low</span>
          <p className="text-red-700 font-semibold">{formatINR(stock.low)}</p>
        </div>
        <div className="bg-gray-50 rounded-xl p-3">
          <span className="text-xs text-gray-500">Volume</span>
          <p className="text-gray-900 font-semibold">{formatNumber(stock.volume)}</p>
        </div>
        <div className="bg-gray-50 rounded-xl p-3">
          <span className="text-xs text-gray-500">Market Cap</span>
          <p className="text-gray-900 font-semibold">{formatMarketCap(stock.market_cap)}</p>
        </div>
      </div>

      {/* Actions */}
      {onAddToWatchlist && (
        <div className="p-5 pt-0">
          <button
            onClick={() => onAddToWatchlist(stock.symbol)}
            className="w-full bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 text-white py-3 px-4 rounded-xl font-semibold transition-all shadow-lg shadow-emerald-500/30 flex items-center justify-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
            </svg>
            <span>Add to Watchlist</span>
          </button>
        </div>
      )}
    </div>
  );
}
