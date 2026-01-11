'use client';

import { useState, useCallback } from 'react';
import { StockQuote, getStockQuote, searchStocks, SearchResult } from '@/lib/api';

interface StockSearchProps {
  onSelectStock: (stock: StockQuote) => void;
}

export default function StockSearch({ onSelectStock }: StockSearchProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingQuote, setLoadingQuote] = useState<string | null>(null);
  const [showResults, setShowResults] = useState(false);

  // Debounce search for better performance
  const handleSearch = useCallback(async (searchQuery: string) => {
    setQuery(searchQuery);
    
    if (searchQuery.length < 1) {
      setResults([]);
      setShowResults(false);
      return;
    }

    setLoading(true);
    try {
      // Fast search without quotes for typeahead
      const data = await searchStocks(searchQuery, false, 20);
      setResults(data);
      setShowResults(true);
    } catch {
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleSelect = async (symbol: string) => {
    setLoadingQuote(symbol);
    try {
      const quote = await getStockQuote(symbol);
      onSelectStock(quote);
      setQuery('');
      setShowResults(false);
    } catch (err) {
      console.error('Failed to get stock quote:', err);
      alert(`Could not fetch data for ${symbol}. Please try again.`);
    } finally {
      setLoadingQuote(null);
    }
  };

  const handleDirectSearch = async () => {
    if (!query.trim()) return;
    
    // Try direct symbol first (with .NS suffix)
    let symbol = query.toUpperCase().trim();
    if (!symbol.endsWith('.NS') && !symbol.endsWith('.BO')) {
      symbol = `${symbol}.NS`;
    }
    
    setLoading(true);
    try {
      const quote = await getStockQuote(symbol);
      onSelectStock(quote);
      setQuery('');
      setShowResults(false);
    } catch {
      // Fall back to search
      await handleSearch(query);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative">
      <div className="flex space-x-3">
        <div className="relative flex-1">
          <input
            type="text"
            value={query}
            onChange={(e) => handleSearch(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleDirectSearch()}
            placeholder="Search all NSE stocks by symbol or company name..."
            className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition"
          />
          {loading && (
            <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
              <div className="w-5 h-5 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
          )}
        </div>
        <button
          onClick={handleDirectSearch}
          disabled={loading}
          className="bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 text-white px-6 py-3 rounded-xl font-semibold transition shadow-lg shadow-emerald-500/30 disabled:opacity-50"
        >
          Search
        </button>
      </div>

      {/* Search Results Dropdown */}
      {showResults && results.length > 0 && (
        <div className="absolute z-50 mt-2 w-full bg-white border border-gray-200 rounded-xl shadow-xl max-h-96 overflow-auto">
          <div className="px-4 py-2 bg-gray-50 border-b border-gray-200 text-sm text-gray-500">
            Found {results.length} NSE stocks. Click to view details.
          </div>
          {results.map((result) => {
            const isLoading = loadingQuote === result.symbol;
            
            return (
              <button
                key={result.symbol}
                onClick={() => handleSelect(result.symbol)}
                disabled={isLoading}
                className="w-full px-4 py-3 text-left hover:bg-emerald-50 transition border-b border-gray-100 last:border-b-0 disabled:opacity-50"
              >
                <div className="flex justify-between items-center">
                  <div className="flex-1 min-w-0">
                    <span className="font-semibold text-gray-900">
                      {result.symbol.replace('.NS', '').replace('.BO', '')}
                    </span>
                    <span className="text-gray-500 text-sm ml-2 truncate block sm:inline">
                      {result.name}
                    </span>
                  </div>
                  <div className="ml-4 flex items-center">
                    {isLoading ? (
                      <div className="w-4 h-4 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
                    ) : (
                      <span className="text-emerald-600 text-sm">
                        NSE
                      </span>
                    )}
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      )}

      {showResults && results.length === 0 && query.length > 0 && !loading && (
        <div className="absolute z-50 mt-2 w-full bg-white border border-gray-200 rounded-xl shadow-xl p-4">
          <div className="text-center text-gray-500 mb-3">
            No matching NSE stocks found for &quot;{query}&quot;
          </div>
          <div className="text-sm text-gray-400">
            <p>Try searching for:</p>
            <ul className="list-disc list-inside mt-1">
              <li>Stock symbol (e.g., RELIANCE, TCS, INFY)</li>
              <li>Company name (e.g., Tata Motors, HDFC Bank)</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
