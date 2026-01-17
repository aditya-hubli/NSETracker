const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface OrderItem {
  product_id: string;
  product_name: string;
  quantity: number;
  unit_price: string;
}

export interface Order {
  id: string;
  user_id: string;
  items: OrderItem[];
  total_amount: string;
  currency: string;
  status: string;
  shipping_address: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface Payment {
  id: string;
  order_id: string;
  user_id: string;
  amount: string;
  currency: string;
  status: string;
  payment_method: string;
  transaction_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface DailySales {
  id: string;
  date: string;
  total_orders: number;
  total_revenue: string;
  total_items_sold: number;
  average_order_value: string;
  completed_payments: number;
  failed_payments: number;
  cancelled_orders: number;
}

// Health check
export async function checkHealth(): Promise<{ status: string }> {
  const res = await fetch(`${API_BASE_URL}/health`);
  return res.json();
}

// Users
export async function getUsers(): Promise<User[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/users/`);
  if (!res.ok) throw new Error('Failed to fetch users');
  return res.json();
}

export async function createUser(data: {
  email: string;
  username: string;
  full_name?: string;
  password: string;
}): Promise<User> {
  const res = await fetch(`${API_BASE_URL}/api/v1/users/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || 'Failed to create user');
  }
  return res.json();
}

export async function updateUser(userId: string, data: {
  email?: string;
  username?: string;
  full_name?: string;
}): Promise<User> {
  const res = await fetch(`${API_BASE_URL}/api/v1/users/${userId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || 'Failed to update user');
  }
  return res.json();
}

// Orders
export async function getOrders(): Promise<Order[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/orders/`);
  if (!res.ok) throw new Error('Failed to fetch orders');
  return res.json();
}

export async function createOrder(data: {
  user_id: string;
  items: OrderItem[];
  shipping_address: string;
  notes?: string;
}): Promise<Order> {
  const res = await fetch(`${API_BASE_URL}/api/v1/orders/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || 'Failed to create order');
  }
  return res.json();
}

export async function cancelOrder(orderId: string): Promise<Order> {
  const res = await fetch(`${API_BASE_URL}/api/v1/orders/${orderId}/cancel`, {
    method: 'POST',
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || 'Failed to cancel order');
  }
  return res.json();
}

// Payments
export async function getPayments(): Promise<Payment[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/payments/`);
  if (!res.ok) throw new Error('Failed to fetch payments');
  return res.json();
}

export async function createPayment(data: {
  order_id: string;
  user_id: string;
  amount: string;
  payment_method?: string;
}): Promise<Payment> {
  const res = await fetch(`${API_BASE_URL}/api/v1/payments/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || 'Failed to create payment');
  }
  return res.json();
}

export async function processPayment(paymentId: string): Promise<Payment> {
  const res = await fetch(`${API_BASE_URL}/api/v1/payments/${paymentId}/process`, {
    method: 'POST',
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || 'Failed to process payment');
  }
  return res.json();
}

export async function refundPayment(paymentId: string): Promise<Payment> {
  const res = await fetch(`${API_BASE_URL}/api/v1/payments/${paymentId}/refund`, {
    method: 'POST',
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || 'Failed to refund payment');
  }
  return res.json();
}

// ============== Stock API ==============

export interface StockQuote {
  symbol: string;
  name: string;
  price: string;
  change: string;
  change_percent: string;
  volume: number;
  market_cap: string | null;
  high: string;
  low: string;
  open: string;
  previous_close: string;
  timestamp: string;
}

export interface StockHistoryPoint {
  date: string;
  open: string;
  high: string;
  low: string;
  close: string;
  volume: number;
}

export interface StockHistory {
  symbol: string;
  period: string;
  interval: string;
  data: StockHistoryPoint[];
}

export interface CompanyInfo {
  symbol: string;
  name: string;
  sector: string | null;
  industry: string | null;
  description: string | null;
  website: string | null;
  employees: number | null;
  country: string | null;
  exchange: string | null;
}

export interface MarketSummary {
  indices: StockQuote[];
  market_status: 'open' | 'closed' | 'pre_market' | 'after_hours';
  timestamp: string;
}

export interface TopMovers {
  gainers: StockQuote[];
  losers: StockQuote[];
  most_active: StockQuote[];
  timestamp: string;
}

export interface Watchlist {
  id: string;
  user_id: string;
  name: string;
  symbols: string[];
  created_at: string;
  updated_at: string;
}

export interface WatchlistWithQuotes {
  id: string;
  user_id: string;
  name: string;
  stocks: StockQuote[];
  created_at: string;
  updated_at: string;
}

// Stock Data
export async function getStockQuote(symbol: string): Promise<StockQuote> {
  const res = await fetch(`${API_BASE_URL}/api/v1/stocks/quote/${symbol}`);
  if (!res.ok) throw new Error(`Failed to fetch quote for ${symbol}`);
  return res.json();
}

export async function getMultipleQuotes(symbols: string[]): Promise<StockQuote[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/stocks/quotes?symbols=${symbols.join(',')}`);
  if (!res.ok) throw new Error('Failed to fetch quotes');
  return res.json();
}

export async function getStockHistory(
  symbol: string,
  period: string = '1mo',
  interval: string = '1d'
): Promise<StockHistory> {
  const res = await fetch(`${API_BASE_URL}/api/v1/stocks/history/${symbol}?period=${period}&interval=${interval}`);
  if (!res.ok) throw new Error(`Failed to fetch history for ${symbol}`);
  return res.json();
}

export async function getCompanyInfo(symbol: string): Promise<CompanyInfo> {
  const res = await fetch(`${API_BASE_URL}/api/v1/stocks/company/${symbol}`);
  if (!res.ok) throw new Error(`Failed to fetch company info for ${symbol}`);
  return res.json();
}

export async function getMarketSummary(): Promise<MarketSummary> {
  const res = await fetch(`${API_BASE_URL}/api/v1/stocks/market/summary`);
  if (!res.ok) throw new Error('Failed to fetch market summary');
  return res.json();
}

export async function getTopMovers(): Promise<TopMovers> {
  const res = await fetch(`${API_BASE_URL}/api/v1/stocks/market/movers`);
  if (!res.ok) throw new Error('Failed to fetch top movers');
  return res.json();
}

export interface SearchResult {
  symbol: string;
  name: string;
  price: string | null;
  change_percent: string | null;
}

export async function searchStocks(query: string, includeQuotes: boolean = false, limit: number = 20): Promise<SearchResult[]> {
  const params = new URLSearchParams({
    q: query,
    limit: limit.toString(),
    include_quotes: includeQuotes.toString(),
  });
  const res = await fetch(`${API_BASE_URL}/api/v1/stocks/search?${params}`);
  if (!res.ok) throw new Error('Failed to search stocks');
  return res.json();
}

export interface NSEStock {
  symbol: string;
  name: string;
}

export interface NSEStockList {
  total_count: number;
  nifty_50: NSEStock[];
  nifty_next_50: NSEStock[];
  categories: {
    nifty_50: number;
    nifty_next_50: number;
    others: number;
  };
}

export async function getAllNSEStocks(): Promise<NSEStockList> {
  const res = await fetch(`${API_BASE_URL}/api/v1/stocks/nse/all`);
  if (!res.ok) throw new Error('Failed to fetch NSE stocks');
  return res.json();
}

export interface Sector {
  name: string;
  stocks: string[];
}

export async function getNSESectors(): Promise<{ sectors: Sector[] }> {
  const res = await fetch(`${API_BASE_URL}/api/v1/stocks/nse/sectors`);
  if (!res.ok) throw new Error('Failed to fetch NSE sectors');
  return res.json();
}

// Watchlists
export async function getUserWatchlists(userId: string): Promise<Watchlist[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/stocks/watchlists/user/${userId}`);
  if (!res.ok) throw new Error('Failed to fetch watchlists');
  return res.json();
}

export async function getWatchlistWithQuotes(watchlistId: string): Promise<WatchlistWithQuotes> {
  const res = await fetch(`${API_BASE_URL}/api/v1/stocks/watchlists/${watchlistId}/quotes`);
  if (!res.ok) throw new Error('Failed to fetch watchlist');
  return res.json();
}

export async function createWatchlist(data: { user_id: string; name: string; symbols?: string[] }): Promise<Watchlist> {
  const res = await fetch(`${API_BASE_URL}/api/v1/stocks/watchlists`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to create watchlist');
  return res.json();
}

export async function addSymbolToWatchlist(watchlistId: string, symbol: string): Promise<Watchlist> {
  const res = await fetch(`${API_BASE_URL}/api/v1/stocks/watchlists/${watchlistId}/symbols/${symbol}`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to add symbol to watchlist');
  return res.json();
}

export async function removeSymbolFromWatchlist(watchlistId: string, symbol: string): Promise<Watchlist> {
  const res = await fetch(`${API_BASE_URL}/api/v1/stocks/watchlists/${watchlistId}/symbols/${symbol}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to remove symbol from watchlist');
  return res.json();
}

// ==============================================
// SENTIMENT API
// ==============================================

export interface SentimentAnalysis {
  symbol: string;
  score: number;
  classification: 'very_negative' | 'negative' | 'neutral' | 'positive' | 'very_positive';
  source: string;
  confidence: number;
  analyzed_at: string;
  sample_size: number;
}

export interface NewsArticle {
  title: string;
  description: string | null;
  url: string;
  source: string;
  published_at: string;
  sentiment_score: number;
  sentiment_classification: string;
}

export interface SocialPost {
  platform: string;
  content: string;
  author: string;
  url: string | null;
  created_at: string;
  upvotes: number;
  comments: number;
  sentiment_score: number;
  sentiment_classification: string;
}

export interface StockSentiment {
  symbol: string;
  overall_score: number;
  overall_classification: string;
  news_sentiment: SentimentAnalysis | null;
  reddit_sentiment: SentimentAnalysis | null;
  twitter_sentiment: SentimentAnalysis | null;
  trending_score: number;
  last_updated: string;
  recent_news: NewsArticle[];
  recent_posts: SocialPost[];
}

export interface TrendingStock {
  symbol: string;
  company_name: string | null;
  mention_count: number;
  sentiment_score: number;
  sentiment_classification: string;
  trending_score: number;
  price_change_percent: number | null;
}

export async function getStockSentiment(symbol: string, refresh: boolean = false): Promise<StockSentiment> {
  const res = await fetch(`${API_BASE_URL}/api/v1/sentiment/stock/${symbol}?refresh=${refresh}`);
  if (!res.ok) throw new Error(`Failed to fetch sentiment for ${symbol}`);
  return res.json();
}

export async function getTrendingStocks(limit: number = 10): Promise<TrendingStock[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/sentiment/trending?limit=${limit}`);
  if (!res.ok) throw new Error('Failed to fetch trending stocks');
  return res.json();
}

export async function getStockNews(symbol: string, days: number = 7): Promise<NewsArticle[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/sentiment/news/${symbol}?days=${days}`);
  if (!res.ok) throw new Error(`Failed to fetch news for ${symbol}`);
  return res.json();
}

export async function getSocialPosts(symbol: string, platform?: string): Promise<SocialPost[]> {
  const url = platform 
    ? `${API_BASE_URL}/api/v1/sentiment/social/${symbol}?platform=${platform}`
    : `${API_BASE_URL}/api/v1/sentiment/social/${symbol}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed to fetch social posts for ${symbol}`);
  return res.json();
}

// ==============================================
// ANALYTICS API
// ==============================================

export interface TechnicalIndicators {
  symbol: string;
  timestamp: string;
  current_price: number | null;
  sma_20: number | null;
  sma_50: number | null;
  sma_200: number | null;
  ema_12: number | null;
  ema_26: number | null;
  macd: number | null;
  macd_signal: number | null;
  macd_histogram: number | null;
  rsi_14: number | null;
  bb_upper: number | null;
  bb_middle: number | null;
  bb_lower: number | null;
  bb_width: number | null;
  volume_sma_20: number | null;
  volume_ratio: number | null;
  atr_14: number | null;
  historical_volatility: number | null;
  support_level: number | null;
  resistance_level: number | null;
}

export interface TradingSignal {
  symbol: string;
  signal: 'strong_buy' | 'buy' | 'neutral' | 'sell' | 'strong_sell';
  confidence: number;
  reasons: string[];
  timestamp: string;
}

export interface VolumeAnalysis {
  symbol: string;
  current_volume: number;
  average_volume_20d: number;
  volume_ratio: number;
  is_unusual: boolean;
  price_volume_correlation: number | null;
}

export interface VolatilityMetrics {
  symbol: string;
  historical_volatility_30d: number;
  historical_volatility_90d: number;
  atr_14: number;
  beta: number | null;
  is_high_volatility: boolean;
}

export interface StockAnalysis {
  symbol: string;
  timestamp: string;
  current_price: number;
  indicators: TechnicalIndicators;
  signal: TradingSignal;
  volume_analysis: VolumeAnalysis;
  volatility: VolatilityMetrics;
  patterns: Array<{ pattern: string; confidence: number; description: string }>;
  key_levels: Record<string, number>;
}

export interface ScreenerResult {
  symbol: string;
  company_name: string | null;
  price: number;
  change_percent: number;
  volume: number;
  rsi: number | null;
  signal: string;
  matched_criteria: string[];
}

export interface HeatmapData {
  symbol: string;
  price: number;
  change_percent: number;
  volume: number;
  volume_ratio: number;
  color: 'green' | 'red';
  intensity: number;
}

export async function getTechnicalIndicators(symbol: string): Promise<TechnicalIndicators> {
  const res = await fetch(`${API_BASE_URL}/api/v1/analytics/indicators/${symbol}`);
  if (!res.ok) throw new Error(`Failed to fetch indicators for ${symbol}`);
  return res.json();
}

export async function getTradingSignal(symbol: string): Promise<TradingSignal> {
  const res = await fetch(`${API_BASE_URL}/api/v1/analytics/signal/${symbol}`);
  if (!res.ok) throw new Error(`Failed to fetch signal for ${symbol}`);
  return res.json();
}

export async function getVolumeAnalysis(symbol: string): Promise<VolumeAnalysis> {
  const res = await fetch(`${API_BASE_URL}/api/v1/analytics/volume/${symbol}`);
  if (!res.ok) throw new Error(`Failed to fetch volume analysis for ${symbol}`);
  return res.json();
}

export async function getVolatilityMetrics(symbol: string): Promise<VolatilityMetrics> {
  const res = await fetch(`${API_BASE_URL}/api/v1/analytics/volatility/${symbol}`);
  if (!res.ok) throw new Error(`Failed to fetch volatility for ${symbol}`);
  return res.json();
}

export async function getFullAnalysis(symbol: string): Promise<StockAnalysis> {
  const res = await fetch(`${API_BASE_URL}/api/v1/analytics/analysis/${symbol}`);
  if (!res.ok) throw new Error(`Failed to fetch analysis for ${symbol}`);
  return res.json();
}

export async function screenStocks(criteria: Record<string, unknown>, symbols?: string[]): Promise<ScreenerResult[]> {
  const url = symbols 
    ? `${API_BASE_URL}/api/v1/analytics/screener?symbols=${symbols.join(',')}`
    : `${API_BASE_URL}/api/v1/analytics/screener`;
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(criteria),
  });
  if (!res.ok) throw new Error('Failed to screen stocks');
  return res.json();
}

export async function getMarketHeatmap(symbols?: string[]): Promise<HeatmapData[]> {
  const url = symbols 
    ? `${API_BASE_URL}/api/v1/analytics/heatmap?symbols=${symbols.join(',')}`
    : `${API_BASE_URL}/api/v1/analytics/heatmap`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch heatmap');
  return res.json();
}

// ==============================================
// NOTIFICATIONS API
// ==============================================

export interface PriceAlert {
  id: string;
  user_id: string;
  symbol: string;
  condition: 'above' | 'below' | 'percent_up' | 'percent_down';
  target_value: number;
  current_price: number | null;
  status: 'active' | 'triggered' | 'expired' | 'cancelled';
  message: string | null;
  created_at: string;
  triggered_at: string | null;
  expires_at: string | null;
}

export interface Notification {
  id: string;
  user_id: string;
  type: string;
  title: string;
  message: string;
  symbol: string | null;
  data: Record<string, unknown> | null;
  read: boolean;
  created_at: string;
}

export async function createPriceAlert(data: {
  symbol: string;
  condition: 'above' | 'below' | 'percent_up' | 'percent_down';
  target_value: number;
  message?: string;
  expires_in_days?: number;
}, userId: string): Promise<PriceAlert> {
  const res = await fetch(`${API_BASE_URL}/api/v1/notifications/alerts?user_id=${userId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to create alert');
  return res.json();
}

export async function getUserAlerts(userId: string, status?: string): Promise<PriceAlert[]> {
  const url = status 
    ? `${API_BASE_URL}/api/v1/notifications/alerts?user_id=${userId}&status=${status}`
    : `${API_BASE_URL}/api/v1/notifications/alerts?user_id=${userId}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch alerts');
  return res.json();
}

export async function cancelAlert(alertId: string, userId: string): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/api/v1/notifications/alerts/${alertId}?user_id=${userId}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to cancel alert');
}

export async function getNotifications(userId: string, unreadOnly: boolean = false): Promise<Notification[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/notifications/?user_id=${userId}&unread_only=${unreadOnly}`);
  if (!res.ok) throw new Error('Failed to fetch notifications');
  return res.json();
}

export async function getUnreadCount(userId: string): Promise<{ unread_count: number }> {
  const res = await fetch(`${API_BASE_URL}/api/v1/notifications/unread-count?user_id=${userId}`);
  if (!res.ok) throw new Error('Failed to fetch unread count');
  return res.json();
}

export async function markNotificationRead(notificationId: string, userId: string): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/api/v1/notifications/${notificationId}/read?user_id=${userId}`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to mark notification as read');
}

export async function markAllNotificationsRead(userId: string): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/api/v1/notifications/read-all?user_id=${userId}`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to mark all notifications as read');
}

// ==============================================
// WEBSOCKET CONNECTION
// ==============================================

export function createWebSocketConnection(userId: string): WebSocket {
  const wsUrl = API_BASE_URL.replace('http', 'ws');
  return new WebSocket(`${wsUrl}/api/v1/notifications/ws/${userId}`);
}
