'use client';

import { StockSentiment, TrendingStock } from '@/lib/api';

interface SentimentGaugeProps {
  score: number;
  classification: string;
  size?: 'sm' | 'md' | 'lg';
}

export function SentimentGauge({ score, classification, size = 'md' }: SentimentGaugeProps) {
  // Convert score (-1 to 1) to percentage (0 to 100)
  const percentage = ((score + 1) / 2) * 100;
  
  const getColor = () => {
    if (score <= -0.6) return 'text-red-500';
    if (score <= -0.2) return 'text-orange-500';
    if (score < 0.2) return 'text-gray-400';
    if (score < 0.6) return 'text-green-400';
    return 'text-green-500';
  };
  
  const getBgColor = () => {
    if (score <= -0.6) return 'bg-red-500';
    if (score <= -0.2) return 'bg-orange-500';
    if (score < 0.2) return 'bg-gray-400';
    if (score < 0.6) return 'bg-green-400';
    return 'bg-green-500';
  };
  
  const sizeClasses = {
    sm: 'h-2 w-24',
    md: 'h-3 w-32',
    lg: 'h-4 w-48',
  };
  
  const textSizes = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
  };
  
  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center gap-2">
        <div className={`${sizeClasses[size]} bg-gray-700 rounded-full overflow-hidden`}>
          <div 
            className={`h-full ${getBgColor()} transition-all duration-500`}
            style={{ width: `${percentage}%` }}
          />
        </div>
        <span className={`${getColor()} ${textSizes[size]} font-semibold`}>
          {score > 0 ? '+' : ''}{score.toFixed(2)}
        </span>
      </div>
      <span className={`${textSizes[size]} text-gray-400 capitalize`}>
        {classification.replace('_', ' ')}
      </span>
    </div>
  );
}

interface SentimentBadgeProps {
  classification: string;
}

export function SentimentBadge({ classification }: SentimentBadgeProps) {
  const colors: Record<string, string> = {
    very_negative: 'bg-red-900 text-red-300 border-red-700',
    negative: 'bg-orange-900 text-orange-300 border-orange-700',
    neutral: 'bg-gray-700 text-gray-300 border-gray-600',
    positive: 'bg-green-900 text-green-300 border-green-700',
    very_positive: 'bg-emerald-900 text-emerald-300 border-emerald-700',
  };
  
  return (
    <span className={`px-2 py-1 text-xs rounded-full border ${colors[classification] || colors.neutral}`}>
      {classification.replace('_', ' ')}
    </span>
  );
}

interface SentimentCardProps {
  sentiment: StockSentiment;
}

export function SentimentCard({ sentiment }: SentimentCardProps) {
  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-white">{sentiment.symbol}</h3>
          <p className="text-sm text-gray-400">Sentiment Analysis</p>
        </div>
        <SentimentBadge classification={sentiment.overall_classification} />
      </div>
      
      <SentimentGauge 
        score={sentiment.overall_score} 
        classification={sentiment.overall_classification}
        size="lg"
      />
      
      <div className="mt-4 grid grid-cols-3 gap-2 text-center">
        {sentiment.news_sentiment && (
          <div className="bg-gray-700/50 rounded p-2">
            <p className="text-xs text-gray-400">News</p>
            <p className={`font-semibold ${sentiment.news_sentiment.score >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {sentiment.news_sentiment.score.toFixed(2)}
            </p>
          </div>
        )}
        {sentiment.reddit_sentiment && (
          <div className="bg-gray-700/50 rounded p-2">
            <p className="text-xs text-gray-400">Reddit</p>
            <p className={`font-semibold ${sentiment.reddit_sentiment.score >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {sentiment.reddit_sentiment.score.toFixed(2)}
            </p>
          </div>
        )}
        <div className="bg-gray-700/50 rounded p-2">
          <p className="text-xs text-gray-400">Trending</p>
          <p className="font-semibold text-blue-400">
            {sentiment.trending_score.toFixed(0)}
          </p>
        </div>
      </div>
    </div>
  );
}

interface TrendingListProps {
  stocks: TrendingStock[];
}

export function TrendingList({ stocks }: TrendingListProps) {
  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700">
      <div className="px-4 py-3 border-b border-gray-700">
        <h3 className="font-semibold text-white flex items-center gap-2">
          <span className="text-orange-500">●</span> Trending Stocks
        </h3>
      </div>
      <div className="divide-y divide-gray-700">
        {stocks.map((stock, index) => (
          <div key={stock.symbol} className="px-4 py-3 flex items-center justify-between hover:bg-gray-700/50 transition-colors">
            <div className="flex items-center gap-3">
              <span className="text-gray-500 text-sm w-5">{index + 1}</span>
              <div>
                <p className="font-medium text-white">{stock.symbol}</p>
                <p className="text-xs text-gray-400">{stock.mention_count} mentions</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <SentimentBadge classification={stock.sentiment_classification} />
              {stock.price_change_percent !== null && (
                <span className={`text-sm ${stock.price_change_percent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {stock.price_change_percent >= 0 ? '+' : ''}{stock.price_change_percent.toFixed(2)}%
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

interface NewsListProps {
  articles: Array<{
    title: string;
    source: string;
    published_at: string;
    sentiment_score: number;
    url: string;
  }>;
}

export function NewsList({ articles }: NewsListProps) {
  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700">
      <div className="px-4 py-3 border-b border-gray-700">
        <h3 className="font-semibold text-white">Recent News</h3>
      </div>
      <div className="divide-y divide-gray-700 max-h-96 overflow-y-auto">
        {articles.map((article, index) => (
          <a 
            key={index} 
            href={article.url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="block px-4 py-3 hover:bg-gray-700/50 transition-colors"
          >
            <div className="flex justify-between items-start gap-2">
              <p className="text-sm text-white line-clamp-2">{article.title}</p>
              <span className={`text-xs font-medium shrink-0 ${
                article.sentiment_score >= 0.2 ? 'text-green-400' : 
                article.sentiment_score <= -0.2 ? 'text-red-400' : 
                'text-gray-400'
              }`}>
                {article.sentiment_score >= 0 ? '+' : ''}{article.sentiment_score.toFixed(2)}
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {article.source} • {new Date(article.published_at).toLocaleDateString()}
            </p>
          </a>
        ))}
      </div>
    </div>
  );
}
