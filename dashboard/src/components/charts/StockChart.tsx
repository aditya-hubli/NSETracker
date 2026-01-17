'use client';

import { useEffect, useRef, useState } from 'react';
import { 
  createChart, 
  ColorType, 
  IChartApi, 
  Time,
  CandlestickData,
  LineData,
  HistogramData,
  CandlestickSeries,
  LineSeries,
  AreaSeries,
  HistogramSeries,
} from 'lightweight-charts';

export type ChartType = 'line' | 'candlestick' | 'area';
export type TimeInterval = '1m' | '5m' | '15m' | '1h' | '1d' | '1w' | '1M';

interface StockChartProps {
  symbol: string;
  height?: number;
  chartType?: ChartType;
  interval?: TimeInterval;
  showVolume?: boolean;
}

interface HistoryDataPoint {
  date: string;
  open: string;
  high: string;
  low: string;
  close: string;
  volume: number;
}

const INTERVAL_MAP: Record<TimeInterval, { period: string; label: string }> = {
  '1m': { period: '1d', label: '1 Minute' },
  '5m': { period: '5d', label: '5 Minutes' },
  '15m': { period: '5d', label: '15 Minutes' },
  '1h': { period: '1mo', label: '1 Hour' },
  '1d': { period: '6mo', label: 'Daily' },
  '1w': { period: '2y', label: 'Weekly' },
  '1M': { period: '5y', label: 'Monthly' },
};

export default function StockChart({
  symbol,
  height = 400,
  chartType = 'candlestick',
  interval = '1d',
  showVolume = true,
}: StockChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPrice, setCurrentPrice] = useState<number | null>(null);
  const [priceChange, setPriceChange] = useState<{ value: number; percent: number } | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Remove existing chart if any
    if (chartRef.current) {
      chartRef.current.remove();
      chartRef.current = null;
    }

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: 'white' },
        textColor: '#333',
        attributionLogo: false,
      },
      grid: {
        vertLines: { color: '#f0f0f0' },
        horzLines: { color: '#f0f0f0' },
      },
      width: chartContainerRef.current.clientWidth,
      height: height,
      timeScale: {
        borderColor: '#e0e0e0',
        timeVisible: true,
        secondsVisible: false,
      },
      rightPriceScale: {
        borderColor: '#e0e0e0',
      },
      crosshair: {
        mode: 1,
        vertLine: {
          width: 1,
          color: '#10b981',
          style: 2,
        },
        horzLine: {
          width: 1,
          color: '#10b981',
          style: 2,
        },
      },
    });

    chartRef.current = chart;

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current && chart) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };
    window.addEventListener('resize', handleResize);

    // Fetch data
    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        const { period } = INTERVAL_MAP[interval];
        const response = await fetch(
          `http://localhost:8000/api/v1/stocks/history/${encodeURIComponent(symbol)}?period=${period}`
        );

        if (!response.ok) throw new Error('Failed to fetch data');

        const data = await response.json();
        const history: HistoryDataPoint[] = data.data || [];

        if (history.length === 0) {
          setError('No data available');
          setLoading(false);
          return;
        }

        // Sort history by date (oldest first) - required by lightweight-charts
        history.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

        // Create series based on chart type using v5 API
        if (chartType === 'candlestick') {
          const series = chart.addSeries(CandlestickSeries, {
            upColor: '#10b981',
            downColor: '#ef4444',
            borderDownColor: '#ef4444',
            borderUpColor: '#10b981',
            wickDownColor: '#ef4444',
            wickUpColor: '#10b981',
          });

          const candleData: CandlestickData<Time>[] = history.map((item) => ({
            time: (new Date(item.date).getTime() / 1000) as Time,
            open: parseFloat(item.open),
            high: parseFloat(item.high),
            low: parseFloat(item.low),
            close: parseFloat(item.close),
          }));

          series.setData(candleData);
        } else if (chartType === 'area') {
          const series = chart.addSeries(AreaSeries, {
            lineColor: '#10b981',
            topColor: 'rgba(16, 185, 129, 0.4)',
            bottomColor: 'rgba(16, 185, 129, 0.0)',
            lineWidth: 2,
          });

          const lineData: LineData<Time>[] = history.map((item) => ({
            time: (new Date(item.date).getTime() / 1000) as Time,
            value: parseFloat(item.close),
          }));

          series.setData(lineData);
        } else {
          // Line chart
          const series = chart.addSeries(LineSeries, {
            color: '#10b981',
            lineWidth: 2,
          });

          const lineData: LineData<Time>[] = history.map((item) => ({
            time: (new Date(item.date).getTime() / 1000) as Time,
            value: parseFloat(item.close),
          }));

          series.setData(lineData);
        }

        // Add volume histogram if enabled
        if (showVolume) {
          const volumeSeries = chart.addSeries(HistogramSeries, {
            color: '#d1d5db',
            priceFormat: {
              type: 'volume',
            },
            priceScaleId: 'volume',
          });

          chart.priceScale('volume').applyOptions({
            scaleMargins: {
              top: 0.8,
              bottom: 0,
            },
          });

          const volumeData: HistogramData<Time>[] = history.map((item, index) => {
            const prevClose = index > 0 ? parseFloat(history[index - 1].close) : parseFloat(item.open);
            const currentClose = parseFloat(item.close);
            return {
              time: (new Date(item.date).getTime() / 1000) as Time,
              value: item.volume,
              color: currentClose >= prevClose ? 'rgba(16, 185, 129, 0.5)' : 'rgba(239, 68, 68, 0.5)',
            };
          });

          volumeSeries.setData(volumeData);
        }

        // Set current price info
        const lastBar = history[history.length - 1];
        const firstBar = history[0];
        const lastPrice = parseFloat(lastBar.close);
        const firstPrice = parseFloat(firstBar.close);
        const change = lastPrice - firstPrice;
        const changePercent = (change / firstPrice) * 100;

        setCurrentPrice(lastPrice);
        setPriceChange({ value: change, percent: changePercent });

        chart.timeScale().fitContent();
        setLoading(false);
      } catch (err) {
        console.error('Chart data fetch error:', err);
        setError('Failed to load chart data');
        setLoading(false);
      }
    };

    fetchData();

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
      chartRef.current = null;
    };
  }, [symbol, chartType, interval, showVolume, height]);

  const formatINR = (value: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
    }).format(value);
  };

  return (
    <div className="relative">
      {loading && (
        <div className="absolute inset-0 bg-white/80 flex items-center justify-center z-10 rounded-xl">
          <div className="flex flex-col items-center">
            <div className="w-10 h-10 border-4 border-emerald-200 border-t-emerald-600 rounded-full animate-spin"></div>
            <span className="text-gray-500 mt-2">Loading chart...</span>
          </div>
        </div>
      )}
      {error && (
        <div className="absolute inset-0 bg-white flex items-center justify-center z-10 rounded-xl">
          <div className="text-center">
            <div className="text-red-500 mb-2">{error}</div>
          </div>
        </div>
      )}
      <div ref={chartContainerRef} className="rounded-xl overflow-hidden" />
      
      {/* Price Info Overlay */}
      {currentPrice && priceChange && (
        <div className="absolute top-4 left-4 bg-white/90 backdrop-blur-sm rounded-lg px-3 py-2 shadow-sm border border-gray-100">
          <div className="flex items-center space-x-3">
            <span className="text-lg font-bold text-gray-900">
              {formatINR(currentPrice)}
            </span>
            <span className={`text-sm font-semibold px-2 py-0.5 rounded ${
              priceChange.percent >= 0 
                ? 'bg-emerald-100 text-emerald-700' 
                : 'bg-red-100 text-red-700'
            }`}>
              {priceChange.percent >= 0 ? '▲' : '▼'} {priceChange.percent >= 0 ? '+' : ''}
              {priceChange.percent.toFixed(2)}%
            </span>
          </div>
          <span className="text-xs text-gray-500">
            {INTERVAL_MAP[interval].label}
          </span>
        </div>
      )}
    </div>
  );
}
