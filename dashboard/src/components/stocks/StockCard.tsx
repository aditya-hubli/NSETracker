import { StockQuote } from '@/lib/api';
import Link from 'next/link';

interface StockCardProps {
  stock: StockQuote;
  onClick?: () => void;
  showDetails?: boolean;
  compact?: boolean;
  linkToDetail?: boolean;
}

export default function StockCard({ stock, onClick, showDetails = true, compact = false, linkToDetail = false }: StockCardProps) {
  const change = parseFloat(stock.change);
  const changePercent = parseFloat(stock.change_percent);
  const isPositive = change >= 0;

  const formatINR = (price: string | number): string => {
    const num = typeof price === 'string' ? parseFloat(price) : price;
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
    }).format(num);
  };

  const formatVolume = (volume: number): string => {
    if (volume >= 10000000) return `${(volume / 10000000).toFixed(2)} Cr`;
    if (volume >= 100000) return `${(volume / 100000).toFixed(2)} L`;
    if (volume >= 1000) return `${(volume / 1000).toFixed(2)} K`;
    return volume.toString();
  };

  // Remove .NS or .BO suffix for display
  const displaySymbol = stock.symbol.replace('.NS', '').replace('.BO', '');

  if (compact) {
    const CompactContent = (
      <div
        onClick={!linkToDetail ? onClick : undefined}
        className={`bg-gray-50 hover:bg-gray-100 rounded-xl p-4 cursor-pointer transition-all border-l-4 ${
          isPositive ? 'border-emerald-500' : 'border-red-500'
        }`}
      >
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-white font-bold text-sm ${
              isPositive ? 'bg-gradient-to-br from-emerald-500 to-green-600' : 'bg-gradient-to-br from-red-500 to-rose-600'
            }`}>
              {displaySymbol.substring(0, 2)}
            </div>
            <div>
              <span className="font-semibold text-gray-900">{displaySymbol}</span>
              <p className="text-xs text-gray-500 truncate max-w-[150px]">{stock.name}</p>
            </div>
          </div>
          <div className="text-right">
            <span className="text-gray-900 font-bold">{formatINR(stock.price)}</span>
            <div className="flex items-center justify-end space-x-1">
              <svg className={`w-3 h-3 ${isPositive ? 'text-emerald-500' : 'text-red-500'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={isPositive ? "M5 10l7-7m0 0l7 7m-7-7v18" : "M19 14l-7 7m0 0l-7-7m7 7V3"} />
              </svg>
              <span className={`text-sm font-semibold ${isPositive ? 'text-emerald-600' : 'text-red-600'}`}>
                {isPositive ? '+' : ''}{changePercent.toFixed(2)}%
              </span>
            </div>
          </div>
        </div>
      </div>
    );

    if (linkToDetail) {
      return <Link href={`/dashboard/stock/${encodeURIComponent(stock.symbol)}`}>{CompactContent}</Link>;
    }
    return CompactContent;
  }

  const FullContent = (
    <div
      onClick={!linkToDetail ? onClick : undefined}
      className={`bg-white hover:shadow-md rounded-2xl p-5 cursor-pointer transition-all border border-gray-100 group`}
    >
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center space-x-3">
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-white font-bold ${
            isPositive ? 'bg-gradient-to-br from-emerald-500 to-green-600' : 'bg-gradient-to-br from-red-500 to-rose-600'
          }`}>
            {displaySymbol.substring(0, 2)}
          </div>
          <div>
            <h3 className="font-bold text-lg text-gray-900 group-hover:text-emerald-600 transition">{displaySymbol}</h3>
            <p className="text-sm text-gray-500 truncate max-w-[180px]">{stock.name}</p>
          </div>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
          isPositive ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'
        }`}>
          {stock.symbol.includes('.NS') ? 'NSE' : stock.symbol.includes('.BO') ? 'BSE' : 'Stock'}
        </span>
      </div>
      
      <div className="flex justify-between items-end">
        <div>
          <p className="text-2xl font-bold text-gray-900">{formatINR(stock.price)}</p>
          <div className="flex items-center mt-1">
            <svg className={`w-4 h-4 ${isPositive ? 'text-emerald-500' : 'text-red-500'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={isPositive ? "M5 10l7-7m0 0l7 7m-7-7v18" : "M19 14l-7 7m0 0l-7-7m7 7V3"} />
            </svg>
            <span className={`text-sm font-semibold ml-1 ${isPositive ? 'text-emerald-600' : 'text-red-600'}`}>
              {isPositive ? '+' : ''}{change.toFixed(2)} ({isPositive ? '+' : ''}{changePercent.toFixed(2)}%)
            </span>
          </div>
        </div>
        
        {showDetails && (
          <div className="text-right text-sm text-gray-500">
            <p>Vol: {formatVolume(stock.volume)}</p>
            <p>H: {formatINR(stock.high)} L: {formatINR(stock.low)}</p>
          </div>
        )}
      </div>
    </div>
  );

  if (linkToDetail) {
    return <Link href={`/dashboard/stock/${encodeURIComponent(stock.symbol)}`}>{FullContent}</Link>;
  }
  return FullContent;
}
