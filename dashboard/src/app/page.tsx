'use client';

import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-white to-green-50">
      {/* Header */}
      <header className="border-b border-gray-100 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-green-600 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-500/30">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <span className="font-bold text-xl text-gray-900">NSE<span className="text-emerald-600">Tracker</span></span>
            </div>
            <div className="flex items-center space-x-4">
              <Link 
                href="/login" 
                className="text-gray-600 hover:text-gray-900 font-medium transition"
              >
                Sign in
              </Link>
              <Link 
                href="/register" 
                className="bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 text-white px-5 py-2.5 rounded-xl font-semibold transition-all shadow-lg shadow-emerald-500/30"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <div className="inline-flex items-center space-x-2 bg-emerald-100 text-emerald-700 px-4 py-2 rounded-full text-sm font-medium mb-6">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span>Live NSE & BSE Market Data</span>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Track Indian Stocks<br />
            <span className="bg-gradient-to-r from-emerald-600 to-green-600 bg-clip-text text-transparent">
              in Real-Time
            </span>
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-10">
            Your comprehensive platform for tracking NIFTY 50, SENSEX, and thousands of NSE & BSE stocks with real-time prices, advanced analytics, and market sentiment.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link 
              href="/register" 
              className="bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-all shadow-lg shadow-emerald-500/30"
            >
              Start Free Today
            </Link>
            <Link 
              href="/login" 
              className="bg-white hover:bg-gray-50 text-gray-700 px-8 py-4 rounded-xl font-semibold text-lg transition border border-gray-200"
            >
              Sign In
            </Link>
          </div>
        </div>

        {/* Market Preview Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-20">
          <div className="bg-white rounded-2xl shadow-xl shadow-emerald-500/10 border border-gray-100 p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <p className="text-gray-500 text-sm">NIFTY 50</p>
                <p className="text-2xl font-bold text-gray-900">₹24,398.45</p>
              </div>
              <span className="bg-emerald-100 text-emerald-700 px-2 py-1 rounded-lg text-sm font-medium">+1.2%</span>
            </div>
            <div className="h-16 flex items-end">
              <svg className="w-full h-full text-emerald-500" viewBox="0 0 100 40">
                <path d="M 0 30 Q 10 25, 20 28 T 40 20 T 60 25 T 80 15 T 100 10" fill="none" stroke="currentColor" strokeWidth="2"/>
              </svg>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-xl shadow-emerald-500/10 border border-gray-100 p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <p className="text-gray-500 text-sm">SENSEX</p>
                <p className="text-2xl font-bold text-gray-900">₹80,218.37</p>
              </div>
              <span className="bg-emerald-100 text-emerald-700 px-2 py-1 rounded-lg text-sm font-medium">+0.8%</span>
            </div>
            <div className="h-16 flex items-end">
              <svg className="w-full h-full text-emerald-500" viewBox="0 0 100 40">
                <path d="M 0 35 Q 15 30, 25 32 T 50 25 T 75 18 T 100 15" fill="none" stroke="currentColor" strokeWidth="2"/>
              </svg>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-xl shadow-emerald-500/10 border border-gray-100 p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <p className="text-gray-500 text-sm">BANK NIFTY</p>
                <p className="text-2xl font-bold text-gray-900">₹52,150.80</p>
              </div>
              <span className="bg-red-100 text-red-700 px-2 py-1 rounded-lg text-sm font-medium">-0.3%</span>
            </div>
            <div className="h-16 flex items-end">
              <svg className="w-full h-full text-red-500" viewBox="0 0 100 40">
                <path d="M 0 15 Q 15 20, 25 18 T 50 25 T 75 22 T 100 30" fill="none" stroke="currentColor" strokeWidth="2"/>
              </svg>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Everything You Need</h2>
          <p className="text-gray-600 max-w-xl mx-auto">Powerful features to help you track and analyze Indian stock markets</p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-white rounded-2xl p-6 border border-gray-100 hover:shadow-lg transition">
            <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="font-bold text-gray-900 text-lg mb-2">Real-Time Data</h3>
            <p className="text-gray-600">Live prices from NSE & BSE exchanges with minimal latency</p>
          </div>

          <div className="bg-white rounded-2xl p-6 border border-gray-100 hover:shadow-lg transition">
            <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="font-bold text-gray-900 text-lg mb-2">Technical Analytics</h3>
            <p className="text-gray-600">RSI, MACD, moving averages and more technical indicators</p>
          </div>

          <div className="bg-white rounded-2xl p-6 border border-gray-100 hover:shadow-lg transition">
            <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="font-bold text-gray-900 text-lg mb-2">Market Sentiment</h3>
            <p className="text-gray-600">AI-powered sentiment analysis from news and social media</p>
          </div>

          <div className="bg-white rounded-2xl p-6 border border-gray-100 hover:shadow-lg transition">
            <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
            </div>
            <h3 className="font-bold text-gray-900 text-lg mb-2">Price Alerts</h3>
            <p className="text-gray-600">Custom notifications when stocks hit your target prices</p>
          </div>

          <div className="bg-white rounded-2xl p-6 border border-gray-100 hover:shadow-lg transition">
            <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
              </svg>
            </div>
            <h3 className="font-bold text-gray-900 text-lg mb-2">Watchlists</h3>
            <p className="text-gray-600">Create and manage personalized stock watchlists</p>
          </div>

          <div className="bg-white rounded-2xl p-6 border border-gray-100 hover:shadow-lg transition">
            <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
              </svg>
            </div>
            <h3 className="font-bold text-gray-900 text-lg mb-2">Market Heatmap</h3>
            <p className="text-gray-600">Visual overview of sector and stock performance</p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-100 bg-white py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 to-green-600 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <span className="font-bold text-gray-900">NSE<span className="text-emerald-600">Tracker</span></span>
            </div>
            <p className="text-gray-500 text-sm">
              © 2024 NSETracker. Real-time Indian stock market data platform.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
