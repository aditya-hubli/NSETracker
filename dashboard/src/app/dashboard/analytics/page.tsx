'use client';

import { useState, useEffect } from 'react';
import { 
  getStockQuote, 
  getStockHistory, 
  StockQuote, 
  StockHistory,
  getTradingSignal,
  getTechnicalIndicators,
  getStockSentiment,
  TradingSignal,
  TechnicalIndicators as BackendIndicators,
  StockSentiment
} from '@/lib/api';

interface TechnicalAnalysis {
  rsi: number;
  rsiSignal: 'oversold' | 'neutral' | 'overbought';
  sma20: number;
  sma50: number;
  trend: 'bullish' | 'bearish' | 'neutral';
  momentum: 'strong' | 'weak' | 'neutral';
  volatility: 'high' | 'medium' | 'low';
  support: number;
  resistance: number;
  recommendation: 'Strong Buy' | 'Buy' | 'Hold' | 'Sell' | 'Strong Sell';
  confidence: number;
  // New: Backend-powered fields
  macd?: number;
  macdSignal?: number;
  ema12?: number;
  ema26?: number;
  bbUpper?: number;
  bbLower?: number;
}

interface SentimentData {
  overall: string;
  score: number;
  newsCount: number;
  trend: string;
}

interface Watchlist {
  id: string;
  name: string;
  symbols: string[];
  createdAt: string;
}

interface StockWithAnalysis {
  symbol: string;
  name: string;
  quote: StockQuote | null;
  analysis: TechnicalAnalysis | null;
  sentiment: SentimentData | null;
  loading: boolean;
  source: 'backend' | 'local';  // Track where analysis came from
}

export default function AnalyticsPage() {
  const [watchlists, setWatchlists] = useState<Watchlist[]>([]);
  const [selectedWatchlist, setSelectedWatchlist] = useState<Watchlist | null>(null);
  const [stocksAnalysis, setStocksAnalysis] = useState<Record<string, StockWithAnalysis>>({});
  const [selectedStock, setSelectedStock] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Load watchlists from localStorage
  useEffect(() => {
    const savedWatchlists = localStorage.getItem('watchlists');
    if (savedWatchlists) {
      const parsed = JSON.parse(savedWatchlists) as Watchlist[];
      setWatchlists(parsed);
      if (parsed.length > 0) {
        setSelectedWatchlist(parsed[0]);
      }
    }
    setLoading(false);
  }, []);

  // Analyze stocks when watchlist changes
  useEffect(() => {
    if (!selectedWatchlist || selectedWatchlist.symbols.length === 0) return;
    
    analyzeWatchlistStocks(selectedWatchlist.symbols);
  }, [selectedWatchlist]);

  async function analyzeWatchlistStocks(symbols: string[]) {
    // Initialize all stocks as loading
    const initial: Record<string, StockWithAnalysis> = {};
    symbols.forEach(symbol => {
      initial[symbol] = {
        symbol,
        name: symbol.replace('.NS', '').replace('.BO', ''),
        quote: null,
        analysis: null,
        sentiment: null,
        loading: true,
        source: 'local',
      };
    });
    setStocksAnalysis(initial);
    
    // If we have a previously selected stock that's in this list, keep it
    if (selectedStock && !symbols.includes(selectedStock)) {
      setSelectedStock(symbols[0] || null);
    } else if (!selectedStock && symbols.length > 0) {
      setSelectedStock(symbols[0]);
    }

    // Analyze each stock - try backend first, fallback to local
    for (const symbol of symbols) {
      try {
        // Try backend API first
        const backendResult = await analyzeWithBackend(symbol);
        
        if (backendResult) {
          setStocksAnalysis(prev => ({
            ...prev,
            [symbol]: backendResult,
          }));
        } else {
          // Fallback to local calculation
          const localResult = await analyzeLocally(symbol);
          setStocksAnalysis(prev => ({
            ...prev,
            [symbol]: localResult,
          }));
        }
      } catch (err) {
        console.error(`Failed to analyze ${symbol}:`, err);
        // Try local fallback on error
        try {
          const localResult = await analyzeLocally(symbol);
          setStocksAnalysis(prev => ({
            ...prev,
            [symbol]: localResult,
          }));
        } catch {
          setStocksAnalysis(prev => ({
            ...prev,
            [symbol]: {
              ...prev[symbol],
              loading: false,
            },
          }));
        }
      }
    }
  }

  // Backend-powered analysis (microservice)
  async function analyzeWithBackend(symbol: string): Promise<StockWithAnalysis | null> {
    try {
      // Fetch from backend analytics service
      const [quoteData, indicators, signal, sentiment] = await Promise.all([
        getStockQuote(symbol),
        getTechnicalIndicators(symbol).catch(() => null),
        getTradingSignal(symbol).catch(() => null),
        getStockSentiment(symbol).catch(() => null),
      ]);

      if (!indicators || !signal) {
        return null; // Fallback to local
      }

      // Map backend response to our interface
      const analysis: TechnicalAnalysis = {
        rsi: indicators.rsi_14 || 50,
        rsiSignal: indicators.rsi_14 ? (indicators.rsi_14 < 30 ? 'oversold' : indicators.rsi_14 > 70 ? 'overbought' : 'neutral') : 'neutral',
        sma20: indicators.sma_20 || 0,
        sma50: indicators.sma_50 || 0,
        trend: determineTrend(indicators, quoteData),
        momentum: determineMomentum(indicators, quoteData),
        volatility: indicators.historical_volatility ? (indicators.historical_volatility > 30 ? 'high' : indicators.historical_volatility < 15 ? 'low' : 'medium') : 'medium',
        support: indicators.support_level || 0,
        resistance: indicators.resistance_level || 0,
        recommendation: mapSignalToRecommendation(signal.signal),
        confidence: signal.confidence * 100,
        // Extended indicators from backend
        macd: indicators.macd || undefined,
        macdSignal: indicators.macd_signal || undefined,
        ema12: indicators.ema_12 || undefined,
        ema26: indicators.ema_26 || undefined,
        bbUpper: indicators.bb_upper || undefined,
        bbLower: indicators.bb_lower || undefined,
      };

      const sentimentData: SentimentData | null = sentiment ? {
        overall: sentiment.overall_classification || 'neutral',
        score: sentiment.overall_score || 0,
        newsCount: sentiment.recent_news?.length || 0,
        trend: sentiment.trending_score > 50 ? 'up' : 'stable',
      } : null;

      return {
        symbol,
        name: quoteData.name || symbol.replace('.NS', '').replace('.BO', ''),
        quote: quoteData,
        analysis,
        sentiment: sentimentData,
        loading: false,
        source: 'backend',
      };
    } catch (err) {
      console.log(`Backend analysis unavailable for ${symbol}, using local:`, err);
      return null;
    }
  }

  // Local fallback analysis (client-side)
  async function analyzeLocally(symbol: string): Promise<StockWithAnalysis> {
    const [quoteData, historyData] = await Promise.all([
      getStockQuote(symbol),
      getStockHistory(symbol, '3mo', '1d'),
    ]);
    
    let analysisResult: TechnicalAnalysis | null = null;
    if (historyData && historyData.data.length > 20) {
      analysisResult = calculateAnalysis(historyData.data, quoteData);
    }

    return {
      symbol,
      name: quoteData.name || symbol.replace('.NS', '').replace('.BO', ''),
      quote: quoteData,
      analysis: analysisResult,
      sentiment: null,
      loading: false,
      source: 'local',
    };
  }

  // Helper functions for backend response mapping
  function determineTrend(indicators: BackendIndicators, quote: StockQuote): 'bullish' | 'bearish' | 'neutral' {
    const price = parseFloat(quote.price);
    const sma20 = indicators.sma_20 || 0;
    const sma50 = indicators.sma_50 || 0;
    
    if (price > sma20 && sma20 > sma50) return 'bullish';
    if (price < sma20 && sma20 < sma50) return 'bearish';
    return 'neutral';
  }

  function determineMomentum(indicators: BackendIndicators, quote: StockQuote): 'strong' | 'weak' | 'neutral' {
    const price = parseFloat(quote.price);
    const sma20 = indicators.sma_20 || price;
    const diff = Math.abs(price - sma20) / sma20;
    
    if (diff > 0.03) return 'strong';
    if (diff < 0.01) return 'weak';
    return 'neutral';
  }

  function mapSignalToRecommendation(signal: string): 'Strong Buy' | 'Buy' | 'Hold' | 'Sell' | 'Strong Sell' {
    const signalMap: Record<string, 'Strong Buy' | 'Buy' | 'Hold' | 'Sell' | 'Strong Sell'> = {
      'STRONG_BUY': 'Strong Buy',
      'BUY': 'Buy',
      'NEUTRAL': 'Hold',
      'SELL': 'Sell',
      'STRONG_SELL': 'Strong Sell',
    };
    return signalMap[signal] || 'Hold';
  }

  function calculateAnalysis(data: StockHistory['data'], currentQuote: StockQuote | null): TechnicalAnalysis {
    const closes = data.map(d => parseFloat(d.close));
    const highs = data.map(d => parseFloat(d.high));
    const lows = data.map(d => parseFloat(d.low));
    const currentPrice = currentQuote ? parseFloat(currentQuote.price) : closes[closes.length - 1];
    
    // Calculate RSI (14-period)
    const gains: number[] = [];
    const losses: number[] = [];
    for (let i = 1; i < closes.length; i++) {
      const diff = closes[i] - closes[i - 1];
      gains.push(diff > 0 ? diff : 0);
      losses.push(diff < 0 ? Math.abs(diff) : 0);
    }
    
    const avgGain = gains.slice(-14).reduce((a, b) => a + b, 0) / 14;
    const avgLoss = losses.slice(-14).reduce((a, b) => a + b, 0) / 14;
    const rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
    const rsi = 100 - (100 / (1 + rs));
    
    // Calculate SMAs
    const sma20 = closes.slice(-20).reduce((a, b) => a + b, 0) / 20;
    const sma50 = closes.slice(-50).reduce((a, b) => a + b, 0) / Math.min(50, closes.length);
    
    // Calculate support and resistance
    const recent30Lows = lows.slice(-30);
    const recent30Highs = highs.slice(-30);
    const support = Math.min(...recent30Lows);
    const resistance = Math.max(...recent30Highs);
    
    // Calculate volatility (standard deviation)
    const mean = closes.slice(-20).reduce((a, b) => a + b, 0) / 20;
    const variance = closes.slice(-20).reduce((a, b) => a + Math.pow(b - mean, 2), 0) / 20;
    const stdDev = Math.sqrt(variance);
    const volatilityPercent = (stdDev / mean) * 100;
    
    // Determine signals
    const rsiSignal: 'oversold' | 'neutral' | 'overbought' = 
      rsi < 30 ? 'oversold' : rsi > 70 ? 'overbought' : 'neutral';
    
    const trend: 'bullish' | 'bearish' | 'neutral' = 
      currentPrice > sma20 && sma20 > sma50 ? 'bullish' :
      currentPrice < sma20 && sma20 < sma50 ? 'bearish' : 'neutral';
    
    const momentum: 'strong' | 'weak' | 'neutral' =
      Math.abs(currentPrice - sma20) / sma20 > 0.03 ? 'strong' :
      Math.abs(currentPrice - sma20) / sma20 < 0.01 ? 'weak' : 'neutral';
    
    const volatility: 'high' | 'medium' | 'low' =
      volatilityPercent > 3 ? 'high' : volatilityPercent < 1.5 ? 'low' : 'medium';
    
    // Calculate recommendation
    let score = 50;
    if (rsi < 30) score += 20;
    else if (rsi < 40) score += 10;
    else if (rsi > 70) score -= 20;
    else if (rsi > 60) score -= 10;
    if (trend === 'bullish') score += 15;
    else if (trend === 'bearish') score -= 15;
    if (currentPrice > sma20) score += 10;
    else score -= 10;
    
    const priceRange = resistance - support;
    const pricePosition = (currentPrice - support) / priceRange;
    if (pricePosition < 0.2) score += 10;
    else if (pricePosition > 0.8) score -= 10;
    
    const recommendation: TechnicalAnalysis['recommendation'] =
      score >= 75 ? 'Strong Buy' :
      score >= 60 ? 'Buy' :
      score >= 40 ? 'Hold' :
      score >= 25 ? 'Sell' : 'Strong Sell';
    
    const confidence = Math.min(95, Math.max(40, 50 + Math.abs(score - 50)));
    
    return {
      rsi: Math.round(rsi * 100) / 100,
      rsiSignal,
      sma20: Math.round(sma20 * 100) / 100,
      sma50: Math.round(sma50 * 100) / 100,
      trend,
      momentum,
      volatility,
      support: Math.round(support * 100) / 100,
      resistance: Math.round(resistance * 100) / 100,
      recommendation,
      confidence,
    };
  }

  const formatINR = (price: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
    }).format(price);
  };

  const getRecommendationColor = (rec: string) => {
    switch (rec) {
      case 'Strong Buy': return 'from-emerald-500 to-green-600';
      case 'Buy': return 'from-green-400 to-emerald-500';
      case 'Hold': return 'from-amber-400 to-orange-500';
      case 'Sell': return 'from-orange-500 to-red-500';
      case 'Strong Sell': return 'from-red-500 to-red-700';
      default: return 'from-gray-400 to-gray-500';
    }
  };

  const getRecommendationBadgeColor = (rec: string) => {
    switch (rec) {
      case 'Strong Buy': return 'bg-emerald-100 text-emerald-700 border-emerald-200';
      case 'Buy': return 'bg-green-100 text-green-700 border-green-200';
      case 'Hold': return 'bg-amber-100 text-amber-700 border-amber-200';
      case 'Sell': return 'bg-orange-100 text-orange-700 border-orange-200';
      case 'Strong Sell': return 'bg-red-100 text-red-700 border-red-200';
      default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const currentStockData = selectedStock ? stocksAnalysis[selectedStock] : null;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading watchlists...</p>
        </div>
      </div>
    );
  }

  if (watchlists.length === 0) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Technical Analysis</h1>
          <p className="text-gray-500 mt-1">Analyze stocks from your watchlists</p>
        </div>
        <div className="bg-white rounded-2xl border border-gray-100 p-10 text-center">
          <div className="w-20 h-20 bg-emerald-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <svg className="w-10 h-10 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">No Watchlists Found</h2>
          <p className="text-gray-500 mb-6">Create a watchlist first to analyze stocks</p>
          <a
            href="/dashboard/watchlist"
            className="inline-flex items-center space-x-2 bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 text-white px-6 py-3 rounded-xl font-semibold transition"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            <span>Create Watchlist</span>
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Technical Analysis</h1>
        <p className="text-gray-500 mt-1">Analyze stocks from your watchlists</p>
      </div>

      {/* Watchlist Selector */}
      <div className="bg-white rounded-2xl border border-gray-100 p-4 shadow-sm">
        <div className="flex flex-wrap gap-2">
          {watchlists.map((watchlist) => (
            <button
              key={watchlist.id}
              onClick={() => setSelectedWatchlist(watchlist)}
              className={`px-4 py-2 rounded-xl font-medium transition flex items-center space-x-2 ${
                selectedWatchlist?.id === watchlist.id
                  ? 'bg-gradient-to-r from-emerald-500 to-green-600 text-white shadow-lg shadow-emerald-500/30'
                  : 'bg-gray-50 text-gray-700 border border-gray-200 hover:border-emerald-300 hover:bg-emerald-50'
              }`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              <span>{watchlist.name}</span>
              <span className={`text-xs px-1.5 py-0.5 rounded-full ${
                selectedWatchlist?.id === watchlist.id ? 'bg-white/20' : 'bg-gray-200'
              }`}>
                {watchlist.symbols.length}
              </span>
            </button>
          ))}
        </div>
      </div>

      {selectedWatchlist && selectedWatchlist.symbols.length === 0 ? (
        <div className="bg-white rounded-2xl border border-gray-100 p-10 text-center">
          <div className="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          </div>
          <p className="text-gray-600 font-medium">No stocks in this watchlist</p>
          <p className="text-gray-400 text-sm mt-1">Add stocks to analyze them</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Stocks List */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
              <div className="p-4 border-b border-gray-100">
                <h2 className="font-semibold text-gray-900">
                  {selectedWatchlist?.name} Stocks
                </h2>
              </div>
              <div className="divide-y divide-gray-100 max-h-[600px] overflow-y-auto">
                {selectedWatchlist?.symbols.map((symbol) => {
                  const stock = stocksAnalysis[symbol];
                  const displaySymbol = symbol.replace('.NS', '').replace('.BO', '');
                  
                  return (
                    <button
                      key={symbol}
                      onClick={() => setSelectedStock(symbol)}
                      className={`w-full p-4 text-left transition ${
                        selectedStock === symbol
                          ? 'bg-emerald-50 border-l-4 border-emerald-500'
                          : 'hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <span className={`font-semibold ${
                            selectedStock === symbol ? 'text-emerald-700' : 'text-gray-900'
                          }`}>
                            {displaySymbol}
                          </span>
                          {stock?.loading ? (
                            <p className="text-xs text-gray-400 mt-1">Analyzing...</p>
                          ) : stock?.analysis ? (
                            <p className={`text-xs font-medium mt-1 ${
                              stock.analysis.recommendation.includes('Buy') ? 'text-emerald-600' :
                              stock.analysis.recommendation.includes('Sell') ? 'text-red-600' : 'text-amber-600'
                            }`}>
                              {stock.analysis.recommendation}
                            </p>
                          ) : (
                            <p className="text-xs text-gray-400 mt-1">No data</p>
                          )}
                        </div>
                        {stock?.quote && !stock.loading && (
                          <div className="text-right">
                            <p className="text-sm font-bold text-gray-900">
                              {formatINR(parseFloat(stock.quote.price))}
                            </p>
                            <p className={`text-xs font-medium ${
                              parseFloat(stock.quote.change_percent) >= 0 ? 'text-emerald-600' : 'text-red-600'
                            }`}>
                              {parseFloat(stock.quote.change_percent) >= 0 ? '+' : ''}
                              {parseFloat(stock.quote.change_percent).toFixed(2)}%
                            </p>
                          </div>
                        )}
                        {stock?.loading && (
                          <div className="w-4 h-4 border-2 border-emerald-300 border-t-emerald-600 rounded-full animate-spin"></div>
                        )}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Analysis Detail */}
          <div className="lg:col-span-3 space-y-6">
            {currentStockData?.loading ? (
              <div className="bg-white rounded-2xl border border-gray-100 p-10 text-center">
                <div className="w-12 h-12 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <p className="text-gray-600">Analyzing {currentStockData.symbol.replace('.NS', '')}...</p>
              </div>
            ) : currentStockData?.analysis && currentStockData?.quote ? (
              <>
                {/* Main Recommendation Card */}
                <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
                  <div className={`bg-gradient-to-r ${getRecommendationColor(currentStockData.analysis.recommendation)} p-6 text-white`}>
                    <div className="flex flex-col lg:flex-row lg:justify-between lg:items-center gap-4">
                      <div>
                        <p className="text-white/80 text-sm font-medium">Analysis for</p>
                        <h2 className="text-2xl font-bold">{currentStockData.name}</h2>
                        <p className="text-white/90 mt-1">{currentStockData.symbol}</p>
                      </div>
                      <div className="text-left lg:text-right">
                        <p className="text-white/80 text-sm">Current Price</p>
                        <p className="text-3xl font-bold">{formatINR(parseFloat(currentStockData.quote.price))}</p>
                        <p className={`text-sm ${parseFloat(currentStockData.quote.change) >= 0 ? 'text-white' : 'text-red-200'}`}>
                          {parseFloat(currentStockData.quote.change) >= 0 ? '+' : ''}{currentStockData.quote.change} ({currentStockData.quote.change_percent}%)
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="p-6">
                    <div className="flex flex-col lg:flex-row gap-6">
                      {/* Recommendation */}
                      <div className="flex-1 text-center p-6 bg-gray-50 rounded-2xl">
                        <p className="text-sm text-gray-500 mb-2">Recommendation</p>
                        <p className={`text-4xl font-bold bg-gradient-to-r ${getRecommendationColor(currentStockData.analysis.recommendation)} bg-clip-text text-transparent`}>
                          {currentStockData.analysis.recommendation}
                        </p>
                        <div className="mt-4">
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full bg-gradient-to-r ${getRecommendationColor(currentStockData.analysis.recommendation)}`}
                              style={{ width: `${currentStockData.analysis.confidence}%` }}
                            ></div>
                          </div>
                          <p className="text-sm text-gray-500 mt-2">{currentStockData.analysis.confidence}% confidence</p>
                        </div>
                      </div>
                      
                      {/* Key Insights */}
                      <div className="flex-1 space-y-4">
                        <h3 className="font-semibold text-gray-900">Key Insights</h3>
                        <div className="space-y-3">
                          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                            <span className="text-gray-600">Trend</span>
                            <span className={`font-semibold capitalize ${
                              currentStockData.analysis.trend === 'bullish' ? 'text-emerald-600' :
                              currentStockData.analysis.trend === 'bearish' ? 'text-red-600' : 'text-gray-600'
                            }`}>
                              {currentStockData.analysis.trend}
                            </span>
                          </div>
                          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                            <span className="text-gray-600">Momentum</span>
                            <span className={`font-semibold capitalize ${
                              currentStockData.analysis.momentum === 'strong' ? 'text-emerald-600' :
                              currentStockData.analysis.momentum === 'weak' ? 'text-amber-600' : 'text-gray-600'
                            }`}>
                              {currentStockData.analysis.momentum}
                            </span>
                          </div>
                          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                            <span className="text-gray-600">Volatility</span>
                            <span className={`font-semibold capitalize ${
                              currentStockData.analysis.volatility === 'high' ? 'text-red-600' :
                              currentStockData.analysis.volatility === 'low' ? 'text-emerald-600' : 'text-amber-600'
                            }`}>
                              {currentStockData.analysis.volatility}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Technical Indicators */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* RSI */}
                  <div className="bg-white rounded-2xl border border-gray-100 p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold text-gray-900">RSI (14)</h3>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        currentStockData.analysis.rsiSignal === 'oversold' ? 'bg-emerald-100 text-emerald-700' :
                        currentStockData.analysis.rsiSignal === 'overbought' ? 'bg-red-100 text-red-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {currentStockData.analysis.rsiSignal}
                      </span>
                    </div>
                    <p className="text-4xl font-bold text-gray-900 mb-4">{currentStockData.analysis.rsi.toFixed(1)}</p>
                    <div className="relative h-3 bg-gradient-to-r from-emerald-500 via-amber-500 to-red-500 rounded-full">
                      <div 
                        className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-white border-2 border-gray-800 rounded-full shadow"
                        style={{ left: `${currentStockData.analysis.rsi}%`, transform: 'translate(-50%, -50%)' }}
                      ></div>
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 mt-2">
                      <span>Oversold</span>
                      <span>Overbought</span>
                    </div>
                  </div>

                  {/* Moving Averages */}
                  <div className="bg-white rounded-2xl border border-gray-100 p-6">
                    <h3 className="font-semibold text-gray-900 mb-4">Moving Averages</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">SMA 20</span>
                        <span className="font-semibold">{formatINR(currentStockData.analysis.sma20)}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">SMA 50</span>
                        <span className="font-semibold">{formatINR(currentStockData.analysis.sma50)}</span>
                      </div>
                      <div className={`mt-4 p-3 rounded-xl ${
                        currentStockData.analysis.trend === 'bullish' ? 'bg-emerald-50' :
                        currentStockData.analysis.trend === 'bearish' ? 'bg-red-50' : 'bg-gray-50'
                      }`}>
                        <p className={`text-sm font-semibold ${
                          currentStockData.analysis.trend === 'bullish' ? 'text-emerald-700' :
                          currentStockData.analysis.trend === 'bearish' ? 'text-red-700' : 'text-gray-700'
                        }`}>
                          {currentStockData.analysis.trend === 'bullish' ? 'Bullish' :
                           currentStockData.analysis.trend === 'bearish' ? 'Bearish' : 'Neutral'}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Support & Resistance */}
                  <div className="bg-white rounded-2xl border border-gray-100 p-6">
                    <h3 className="font-semibold text-gray-900 mb-4">Support & Resistance</h3>
                    <div className="space-y-3">
                      <div className="p-3 bg-red-50 rounded-xl">
                        <p className="text-xs text-red-600 font-medium">RESISTANCE</p>
                        <p className="text-xl font-bold text-red-700">{formatINR(currentStockData.analysis.resistance)}</p>
                      </div>
                      <div className="p-3 bg-gray-100 rounded-xl text-center">
                        <p className="text-xs text-gray-500">CURRENT</p>
                        <p className="text-lg font-bold text-gray-900">{formatINR(parseFloat(currentStockData.quote.price))}</p>
                      </div>
                      <div className="p-3 bg-emerald-50 rounded-xl">
                        <p className="text-xs text-emerald-600 font-medium">SUPPORT</p>
                        <p className="text-xl font-bold text-emerald-700">{formatINR(currentStockData.analysis.support)}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="bg-white rounded-2xl border border-gray-100 p-10 text-center">
                <div className="w-16 h-16 bg-emerald-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                </div>
                <p className="text-gray-900 font-semibold">Select a Stock</p>
                <p className="text-gray-500 text-sm mt-1">Click on a stock to view its analysis</p>
              </div>
            )}

            {/* Summary Table */}
            {selectedWatchlist && Object.keys(stocksAnalysis).length > 0 && (
              <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
                <div className="p-5 border-b border-gray-100">
                  <h3 className="font-semibold text-gray-900">{selectedWatchlist.name} Summary</h3>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Stock</th>
                        <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase">Price</th>
                        <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase">Change</th>
                        <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase">RSI</th>
                        <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase">Trend</th>
                        <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase">Recommendation</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {selectedWatchlist.symbols.map((symbol) => {
                        const stock = stocksAnalysis[symbol];
                        const displaySymbol = symbol.replace('.NS', '').replace('.BO', '');
                        
                        if (stock?.loading) {
                          return (
                            <tr key={symbol} className="hover:bg-gray-50">
                              <td className="px-4 py-3 font-medium text-gray-900">{displaySymbol}</td>
                              <td colSpan={5} className="px-4 py-3 text-center text-gray-400">
                                <div className="flex items-center justify-center space-x-2">
                                  <div className="w-4 h-4 border-2 border-emerald-300 border-t-emerald-600 rounded-full animate-spin"></div>
                                  <span>Analyzing...</span>
                                </div>
                              </td>
                            </tr>
                          );
                        }
                        
                        if (!stock?.quote || !stock?.analysis) {
                          return (
                            <tr key={symbol} className="hover:bg-gray-50">
                              <td className="px-4 py-3 font-medium text-gray-900">{displaySymbol}</td>
                              <td colSpan={5} className="px-4 py-3 text-center text-gray-400">No data</td>
                            </tr>
                          );
                        }
                        
                        const changePercent = parseFloat(stock.quote.change_percent);
                        
                        return (
                          <tr 
                            key={symbol} 
                            className={`hover:bg-gray-50 cursor-pointer ${selectedStock === symbol ? 'bg-emerald-50' : ''}`}
                            onClick={() => setSelectedStock(symbol)}
                          >
                            <td className="px-4 py-3 font-medium text-gray-900">{displaySymbol}</td>
                            <td className="px-4 py-3 text-right font-semibold">{formatINR(parseFloat(stock.quote.price))}</td>
                            <td className={`px-4 py-3 text-right font-semibold ${changePercent >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                              {changePercent >= 0 ? '+' : ''}{changePercent.toFixed(2)}%
                            </td>
                            <td className="px-4 py-3 text-center">
                              <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${
                                stock.analysis.rsiSignal === 'oversold' ? 'bg-emerald-100 text-emerald-700' :
                                stock.analysis.rsiSignal === 'overbought' ? 'bg-red-100 text-red-700' :
                                'bg-gray-100 text-gray-700'
                              }`}>
                                {stock.analysis.rsi.toFixed(0)}
                              </span>
                            </td>
                            <td className="px-4 py-3 text-center">
                              <span className={`capitalize font-medium ${
                                stock.analysis.trend === 'bullish' ? 'text-emerald-600' :
                                stock.analysis.trend === 'bearish' ? 'text-red-600' : 'text-gray-600'
                              }`}>
                                {stock.analysis.trend}
                              </span>
                            </td>
                            <td className="px-4 py-3 text-center">
                              <span className={`inline-flex px-3 py-1 rounded-full text-xs font-semibold border ${getRecommendationBadgeColor(stock.analysis.recommendation)}`}>
                                {stock.analysis.recommendation}
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
