'use client';

import { TechnicalIndicators, TradingSignal, HeatmapData } from '@/lib/api';

interface SignalBadgeProps {
  signal: string;
  confidence?: number;
}

export function SignalBadge({ signal, confidence }: SignalBadgeProps) {
  const colors: Record<string, string> = {
    strong_buy: 'bg-emerald-900 text-emerald-300 border-emerald-700',
    buy: 'bg-green-900 text-green-300 border-green-700',
    neutral: 'bg-gray-700 text-gray-300 border-gray-600',
    sell: 'bg-orange-900 text-orange-300 border-orange-700',
    strong_sell: 'bg-red-900 text-red-300 border-red-700',
  };
  
  const labels: Record<string, string> = {
    strong_buy: 'STRONG BUY',
    buy: 'BUY',
    neutral: 'NEUTRAL',
    sell: 'SELL',
    strong_sell: 'STRONG SELL',
  };
  
  return (
    <div className="flex items-center gap-2">
      <span className={`px-3 py-1 text-sm font-bold rounded border ${colors[signal] || colors.neutral}`}>
        {labels[signal] || signal.toUpperCase()}
      </span>
      {confidence !== undefined && (
        <span className="text-xs text-gray-400">
          {(confidence * 100).toFixed(0)}% confidence
        </span>
      )}
    </div>
  );
}

interface IndicatorRowProps {
  label: string;
  value: number | null;
  suffix?: string;
  highlight?: 'positive' | 'negative' | 'neutral';
}

function IndicatorRow({ label, value, suffix = '', highlight }: IndicatorRowProps) {
  const getColor = () => {
    if (!highlight) return 'text-white';
    if (highlight === 'positive') return 'text-green-400';
    if (highlight === 'negative') return 'text-red-400';
    return 'text-gray-400';
  };
  
  return (
    <div className="flex justify-between items-center py-1">
      <span className="text-gray-400 text-sm">{label}</span>
      <span className={`font-mono text-sm ${getColor()}`}>
        {value !== null ? `${value.toFixed(2)}${suffix}` : 'N/A'}
      </span>
    </div>
  );
}

interface TechnicalIndicatorsCardProps {
  indicators: TechnicalIndicators;
  currentPrice?: number;
}

export function TechnicalIndicatorsCard({ indicators, currentPrice }: TechnicalIndicatorsCardProps) {
  const price = currentPrice || indicators.current_price || 0;
  
  const getPriceVsSMA = (sma: number | null) => {
    if (!sma || !price) return 'neutral';
    return price > sma ? 'positive' : 'negative';
  };
  
  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700">
      <div className="px-4 py-3 border-b border-gray-700">
        <h3 className="font-semibold text-white">Technical Indicators</h3>
        <p className="text-sm text-gray-400">{indicators.symbol}</p>
      </div>
      
      <div className="p-4 space-y-4">
        {/* Moving Averages */}
        <div>
          <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">Moving Averages</h4>
          <IndicatorRow 
            label="SMA 20" 
            value={indicators.sma_20} 
            highlight={getPriceVsSMA(indicators.sma_20)}
          />
          <IndicatorRow 
            label="SMA 50" 
            value={indicators.sma_50}
            highlight={getPriceVsSMA(indicators.sma_50)}
          />
          <IndicatorRow 
            label="SMA 200" 
            value={indicators.sma_200}
            highlight={getPriceVsSMA(indicators.sma_200)}
          />
        </div>
        
        {/* RSI */}
        <div>
          <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">Momentum</h4>
          <div className="flex justify-between items-center py-1">
            <span className="text-gray-400 text-sm">RSI (14)</span>
            <div className="flex items-center gap-2">
              <span className={`font-mono text-sm ${
                (indicators.rsi_14 || 50) < 30 ? 'text-green-400' : 
                (indicators.rsi_14 || 50) > 70 ? 'text-red-400' : 
                'text-white'
              }`}>
                {indicators.rsi_14?.toFixed(1) || 'N/A'}
              </span>
              {indicators.rsi_14 && (
                <span className="text-xs text-gray-500">
                  {indicators.rsi_14 < 30 ? '(Oversold)' : 
                   indicators.rsi_14 > 70 ? '(Overbought)' : ''}
                </span>
              )}
            </div>
          </div>
        </div>
        
        {/* MACD */}
        <div>
          <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">MACD</h4>
          <IndicatorRow 
            label="MACD" 
            value={indicators.macd}
            highlight={indicators.macd && indicators.macd > 0 ? 'positive' : 'negative'}
          />
          <IndicatorRow label="Signal" value={indicators.macd_signal} />
          <IndicatorRow 
            label="Histogram" 
            value={indicators.macd_histogram}
            highlight={indicators.macd_histogram && indicators.macd_histogram > 0 ? 'positive' : 'negative'}
          />
        </div>
        
        {/* Bollinger Bands */}
        <div>
          <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">Bollinger Bands</h4>
          <IndicatorRow label="Upper" value={indicators.bb_upper} />
          <IndicatorRow label="Middle" value={indicators.bb_middle} />
          <IndicatorRow label="Lower" value={indicators.bb_lower} />
        </div>
        
        {/* Support/Resistance */}
        <div>
          <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">Key Levels</h4>
          <IndicatorRow label="Support" value={indicators.support_level} highlight="positive" />
          <IndicatorRow label="Resistance" value={indicators.resistance_level} highlight="negative" />
        </div>
      </div>
    </div>
  );
}

interface TradingSignalCardProps {
  signal: TradingSignal;
}

export function TradingSignalCard({ signal }: TradingSignalCardProps) {
  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="font-semibold text-white">{signal.symbol}</h3>
          <p className="text-xs text-gray-400">Trading Signal</p>
        </div>
        <SignalBadge signal={signal.signal} confidence={signal.confidence} />
      </div>
      
      {signal.reasons.length > 0 && (
        <div>
          <p className="text-xs text-gray-500 mb-2">Analysis:</p>
          <ul className="space-y-1">
            {signal.reasons.map((reason, index) => (
              <li key={index} className="text-sm text-gray-300 flex items-start gap-2">
                <span className="text-blue-400">•</span>
                {reason}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

interface MarketHeatmapProps {
  data: HeatmapData[];
}

export function MarketHeatmap({ data }: MarketHeatmapProps) {
  // Sort by absolute change
  const sortedData = [...data].sort((a, b) => Math.abs(b.change_percent) - Math.abs(a.change_percent));
  
  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700">
      <div className="px-4 py-3 border-b border-gray-700">
        <h3 className="font-semibold text-white">Market Heatmap</h3>
      </div>
      <div className="p-4">
        <div className="grid grid-cols-5 gap-2">
          {sortedData.map((stock) => {
            const intensity = Math.min(Math.abs(stock.change_percent) / 3, 1);
            const bgColor = stock.change_percent >= 0 
              ? `rgba(34, 197, 94, ${0.2 + intensity * 0.6})` 
              : `rgba(239, 68, 68, ${0.2 + intensity * 0.6})`;
            
            return (
              <div
                key={stock.symbol}
                className="p-3 rounded-lg text-center transition-transform hover:scale-105 cursor-pointer"
                style={{ backgroundColor: bgColor }}
              >
                <p className="font-bold text-white text-sm">{stock.symbol}</p>
                <p className={`text-xs font-mono ${stock.change_percent >= 0 ? 'text-green-300' : 'text-red-300'}`}>
                  {stock.change_percent >= 0 ? '+' : ''}{stock.change_percent.toFixed(2)}%
                </p>
                <p className="text-xs text-gray-300">${stock.price.toFixed(2)}</p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

interface ScreenerTableProps {
  results: Array<{
    symbol: string;
    price: number;
    change_percent: number;
    volume: number;
    rsi: number | null;
    signal: string;
    matched_criteria: string[];
  }>;
}

export function ScreenerTable({ results }: ScreenerTableProps) {
  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-700">
        <h3 className="font-semibold text-white">Screener Results</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-700/50">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-semibold text-gray-400">Symbol</th>
              <th className="px-4 py-2 text-right text-xs font-semibold text-gray-400">Price</th>
              <th className="px-4 py-2 text-right text-xs font-semibold text-gray-400">Change</th>
              <th className="px-4 py-2 text-right text-xs font-semibold text-gray-400">Volume</th>
              <th className="px-4 py-2 text-right text-xs font-semibold text-gray-400">RSI</th>
              <th className="px-4 py-2 text-center text-xs font-semibold text-gray-400">Signal</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700">
            {results.map((stock) => (
              <tr key={stock.symbol} className="hover:bg-gray-700/30 transition-colors">
                <td className="px-4 py-3">
                  <span className="font-medium text-white">{stock.symbol}</span>
                </td>
                <td className="px-4 py-3 text-right font-mono text-white">
                  ${stock.price.toFixed(2)}
                </td>
                <td className={`px-4 py-3 text-right font-mono ${stock.change_percent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {stock.change_percent >= 0 ? '+' : ''}{stock.change_percent.toFixed(2)}%
                </td>
                <td className="px-4 py-3 text-right text-gray-400">
                  {(stock.volume / 1000000).toFixed(2)}M
                </td>
                <td className="px-4 py-3 text-right">
                  <span className={`font-mono ${
                    (stock.rsi || 50) < 30 ? 'text-green-400' : 
                    (stock.rsi || 50) > 70 ? 'text-red-400' : 
                    'text-gray-400'
                  }`}>
                    {stock.rsi?.toFixed(1) || 'N/A'}
                  </span>
                </td>
                <td className="px-4 py-3 text-center">
                  <SignalBadge signal={stock.signal} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
