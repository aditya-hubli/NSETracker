'use client';

import { useState, useEffect } from 'react';
import { searchStocks, SearchResult } from '@/lib/api';

interface NewsArticle {
  title: string;
  description: string | null;
  url: string;
  source: string;
  published_at: string;
  sentiment?: {
    label: string;
    score: number;
  };
}

interface StockNews {
  symbol: string;
  news: NewsArticle[];
  overall_sentiment: string;
  sentiment_score: number;
}

export default function NewsPage() {
  const [selectedSymbol, setSelectedSymbol] = useState<string>('RELIANCE.NS');
  const [news, setNews] = useState<StockNews | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searchLoading, setSearchLoading] = useState(false);

  const fetchNews = async (symbol: string) => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/sentiment/${encodeURIComponent(symbol)}/news`
      );
      if (response.ok) {
        const data = await response.json();
        setNews(data);
      } else {
        setNews(null);
      }
    } catch (err) {
      console.error('Failed to fetch news:', err);
      setNews(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNews(selectedSymbol);
  }, [selectedSymbol]);

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

  const getSentimentColor = (label: string) => {
    switch (label.toLowerCase()) {
      case 'positive':
      case 'very_positive':
        return 'text-emerald-600 bg-emerald-50';
      case 'negative':
      case 'very_negative':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const getSentimentIcon = (label: string) => {
    switch (label.toLowerCase()) {
      case 'very_positive':
      case 'positive':
        return '▲';
      case 'negative':
      case 'very_negative':
        return '▼';
      default:
        return '—';
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(hours / 24);

    if (hours < 1) return 'Just now';
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
  };

  const TRENDING_STOCKS = [
    { symbol: 'RELIANCE.NS', name: 'Reliance' },
    { symbol: 'TCS.NS', name: 'TCS' },
    { symbol: 'HDFCBANK.NS', name: 'HDFC Bank' },
    { symbol: 'INFY.NS', name: 'Infosys' },
    { symbol: 'TATAMOTORS.NS', name: 'Tata Motors' },
    { symbol: 'ADANIENT.NS', name: 'Adani Ent' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Market News</h1>
        <p className="text-gray-500 mt-1">Latest news with AI-powered sentiment analysis</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar - Stock Selection */}
        <div className="lg:col-span-1 space-y-4">
          {/* Search */}
          <div className="bg-white border border-gray-100 rounded-2xl p-4 shadow-sm">
            <h3 className="font-semibold text-gray-900 mb-3">Search Stock</h3>
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                placeholder="Search stocks..."
                className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-gray-900 text-sm"
              />
              {searchLoading && (
                <div className="absolute right-3 top-1/2 -translate-y-1/2">
                  <div className="w-4 h-4 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
                </div>
              )}
            </div>
            {searchResults.length > 0 && (
              <div className="mt-2 border border-gray-200 rounded-xl overflow-hidden">
                {searchResults.map((result) => (
                  <button
                    key={result.symbol}
                    onClick={() => {
                      setSelectedSymbol(result.symbol);
                      setSearchQuery('');
                      setSearchResults([]);
                    }}
                    className="w-full px-3 py-2 text-left hover:bg-emerald-50 border-b border-gray-100 last:border-b-0 text-sm"
                  >
                    <span className="font-medium text-gray-900">
                      {result.symbol.replace('.NS', '')}
                    </span>
                    <span className="text-gray-500 ml-2 text-xs">{result.name}</span>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Trending Stocks */}
          <div className="bg-white border border-gray-100 rounded-2xl p-4 shadow-sm">
            <h3 className="font-semibold text-gray-900 mb-3">Trending</h3>
            <div className="space-y-2">
              {TRENDING_STOCKS.map((stock) => (
                <button
                  key={stock.symbol}
                  onClick={() => setSelectedSymbol(stock.symbol)}
                  className={`w-full px-3 py-2 rounded-xl text-left transition text-sm ${
                    selectedSymbol === stock.symbol
                      ? 'bg-emerald-100 text-emerald-700 font-medium'
                      : 'hover:bg-gray-50 text-gray-700'
                  }`}
                >
                  {stock.name}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Main Content - News Feed */}
        <div className="lg:col-span-3">
          {/* Selected Stock Header */}
          <div className="bg-white border border-gray-100 rounded-2xl p-5 shadow-sm mb-6">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">
                  {selectedSymbol.replace('.NS', '').replace('.BO', '')}
                </h2>
                <p className="text-gray-500">Latest news and sentiment</p>
              </div>
              {news && (
                <div className={`px-4 py-2 rounded-xl ${getSentimentColor(news.overall_sentiment)}`}>
                  <span className="font-bold mr-2">{getSentimentIcon(news.overall_sentiment)}</span>
                  <span className="font-semibold capitalize">
                    {news.overall_sentiment.replace('_', ' ')}
                  </span>
                  <span className="ml-2 text-sm opacity-75">
                    ({(news.sentiment_score * 100).toFixed(0)}%)
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* News Articles */}
          {loading ? (
            <div className="bg-white border border-gray-100 rounded-2xl p-10 text-center shadow-sm">
              <div className="animate-spin rounded-full h-12 w-12 border-4 border-emerald-200 border-t-emerald-600 mx-auto"></div>
              <p className="text-gray-500 mt-4">Loading news...</p>
            </div>
          ) : news && news.news.length > 0 ? (
            <div className="space-y-4">
              {news.news.map((article, index) => (
                <a
                  key={index}
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block bg-white border border-gray-100 rounded-2xl p-5 shadow-sm hover:shadow-md transition hover:border-emerald-200"
                >
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 hover:text-emerald-600 transition line-clamp-2">
                        {article.title}
                      </h3>
                      <div className="flex items-center space-x-3 mt-2 text-sm text-gray-500">
                        <span className="font-medium">{article.source || 'News'}</span>
                        <span>•</span>
                        <span>{formatDate(article.published_at)}</span>
                      </div>
                    </div>
                    {article.sentiment && (
                      <span className={`px-3 py-1 rounded-lg text-sm font-medium whitespace-nowrap ml-4 ${getSentimentColor(article.sentiment.label)}`}>
                        {getSentimentIcon(article.sentiment.label)} {article.sentiment.label.replace('_', ' ')}
                      </span>
                    )}
                  </div>
                  {article.description && (
                    <p className="text-gray-600 line-clamp-2">{article.description}</p>
                  )}
                  <div className="mt-3 text-emerald-600 text-sm font-medium flex items-center">
                    Read more
                    <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </a>
              ))}
            </div>
          ) : (
            <div className="bg-white border border-gray-100 rounded-2xl p-10 text-center shadow-sm">
              <div className="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                </svg>
              </div>
              <p className="text-gray-600 font-medium">No news available</p>
              <p className="text-gray-400 text-sm mt-1">Try selecting a different stock</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
