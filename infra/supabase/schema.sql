-- ==============================================
-- EVENT-DRIVEN DATA PLATFORM - DATABASE SCHEMA
-- ==============================================
-- Supabase PostgreSQL Schema
-- Version: 1.0.0
-- ==============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable TimescaleDB for time-series data (if available)
-- CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ==============================================
-- 0. USERS TABLE
-- ==============================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_is_active ON users(is_active);

-- ==============================================
-- 0.1. ORDERS TABLE
-- ==============================================
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    items JSONB NOT NULL DEFAULT '[]'::jsonb,
    total_amount DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(20) DEFAULT 'pending',
    shipping_address TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_order_status CHECK (status IN ('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled')),
    CONSTRAINT positive_total CHECK (total_amount >= 0)
);

CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at DESC);

-- ==============================================
-- 0.2. PAYMENTS TABLE
-- ==============================================
CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES orders(id),
    user_id UUID NOT NULL REFERENCES users(id),
    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(20) DEFAULT 'pending',
    payment_method VARCHAR(20) DEFAULT 'card',
    transaction_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_payment_status CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'refunded')),
    CONSTRAINT valid_payment_method CHECK (payment_method IN ('card', 'bank_transfer', 'paypal', 'crypto')),
    CONSTRAINT positive_amount CHECK (amount >= 0)
);

CREATE INDEX idx_payments_order_id ON payments(order_id);
CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_created_at ON payments(created_at DESC);

-- ==============================================
-- 1. DAILY SALES AGGREGATION TABLE
-- ==============================================
CREATE TABLE IF NOT EXISTS daily_sales (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL,
    total_orders INTEGER DEFAULT 0,
    total_revenue DECIMAL(15, 2) DEFAULT 0.00,
    total_items_sold INTEGER DEFAULT 0,
    average_order_value DECIMAL(15, 2) DEFAULT 0.00,
    completed_payments INTEGER DEFAULT 0,
    failed_payments INTEGER DEFAULT 0,
    cancelled_orders INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_daily_sales_date UNIQUE(date),
    CONSTRAINT positive_revenue CHECK (total_revenue >= 0),
    CONSTRAINT positive_orders CHECK (total_orders >= 0)
);

-- Index for fast date-based queries
CREATE INDEX idx_daily_sales_date ON daily_sales(date DESC);

-- ==============================================
-- 2. USER ACTIVITY AGGREGATION TABLE
-- ==============================================
CREATE TABLE IF NOT EXISTS user_activity (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    hour_bucket TIMESTAMP WITH TIME ZONE NOT NULL,
    event_count INTEGER DEFAULT 0,
    event_types JSONB DEFAULT '[]'::jsonb,
    last_activity TIMESTAMP WITH TIME ZONE,
    first_activity TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_user_hour UNIQUE(user_id, hour_bucket),
    CONSTRAINT positive_event_count CHECK (event_count >= 0)
);

-- Indexes for fast queries
CREATE INDEX idx_user_activity_user_id ON user_activity(user_id);
CREATE INDEX idx_user_activity_hour_bucket ON user_activity(hour_bucket DESC);
CREATE INDEX idx_user_activity_last_activity ON user_activity(last_activity DESC);

-- ==============================================
-- 3. FRAUD SIGNALS TABLE
-- ==============================================
CREATE TABLE IF NOT EXISTS fraud_signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    window_start TIMESTAMP WITH TIME ZONE NOT NULL,
    window_end TIMESTAMP WITH TIME ZONE NOT NULL,
    user_id VARCHAR(255),
    payment_id VARCHAR(255),
    order_id VARCHAR(255),
    signal_type VARCHAR(50) NOT NULL, -- 'multiple_failures', 'high_frequency', 'unusual_amount'
    failed_payment_count INTEGER DEFAULT 0,
    total_amount DECIMAL(15, 2) DEFAULT 0.00,
    risk_score DECIMAL(5, 2) DEFAULT 0.00, -- 0 to 100
    metadata JSONB DEFAULT '{}'::jsonb,
    is_reviewed BOOLEAN DEFAULT FALSE,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_window CHECK (window_end > window_start),
    CONSTRAINT valid_risk_score CHECK (risk_score >= 0 AND risk_score <= 100)
);

-- Indexes for fraud detection queries
CREATE INDEX idx_fraud_signals_window_start ON fraud_signals(window_start DESC);
CREATE INDEX idx_fraud_signals_user_id ON fraud_signals(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX idx_fraud_signals_signal_type ON fraud_signals(signal_type);
CREATE INDEX idx_fraud_signals_is_reviewed ON fraud_signals(is_reviewed);
CREATE INDEX idx_fraud_signals_risk_score ON fraud_signals(risk_score DESC);

-- ==============================================
-- 4. RAW EVENTS TABLE (Optional - for debugging)
-- ==============================================
CREATE TABLE IF NOT EXISTS raw_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id VARCHAR(255) UNIQUE NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    topic VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Partitioning by month for performance
    PARTITION BY RANGE (timestamp)
);

-- Create partitions for current and next 3 months
CREATE TABLE IF NOT EXISTS raw_events_2025_12 PARTITION OF raw_events
    FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');

CREATE TABLE IF NOT EXISTS raw_events_2026_01 PARTITION OF raw_events
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE IF NOT EXISTS raw_events_2026_02 PARTITION OF raw_events
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

CREATE TABLE IF NOT EXISTS raw_events_2026_03 PARTITION OF raw_events
    FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');

-- Indexes for raw events
CREATE INDEX idx_raw_events_event_type ON raw_events(event_type);
CREATE INDEX idx_raw_events_topic ON raw_events(topic);
CREATE INDEX idx_raw_events_timestamp ON raw_events(timestamp DESC);

-- ==============================================
-- 5. FUNCTIONS & TRIGGERS
-- ==============================================

-- Function to update 'updated_at' timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for daily_sales
CREATE TRIGGER update_daily_sales_updated_at
    BEFORE UPDATE ON daily_sales
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for user_activity
CREATE TRIGGER update_user_activity_updated_at
    BEFORE UPDATE ON user_activity
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ==============================================
-- 6. VIEWS FOR ANALYTICS
-- ==============================================

-- View: Recent sales performance (last 30 days)
CREATE OR REPLACE VIEW v_recent_sales_performance AS
SELECT 
    date,
    total_orders,
    total_revenue,
    average_order_value,
    completed_payments,
    failed_payments,
    CASE 
        WHEN (completed_payments + failed_payments) > 0 
        THEN ROUND((completed_payments::DECIMAL / (completed_payments + failed_payments) * 100), 2)
        ELSE 0 
    END AS payment_success_rate
FROM daily_sales
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY date DESC;

-- View: Top active users (last 7 days)
CREATE OR REPLACE VIEW v_top_active_users AS
SELECT 
    user_id,
    SUM(event_count) AS total_events,
    MAX(last_activity) AS last_seen,
    MIN(first_activity) AS first_seen
FROM user_activity
WHERE hour_bucket >= NOW() - INTERVAL '7 days'
GROUP BY user_id
ORDER BY total_events DESC
LIMIT 100;

-- View: High-risk fraud signals (unreviewed)
CREATE OR REPLACE VIEW v_high_risk_fraud AS
SELECT 
    id,
    user_id,
    payment_id,
    signal_type,
    risk_score,
    failed_payment_count,
    total_amount,
    window_start,
    created_at
FROM fraud_signals
WHERE is_reviewed = FALSE 
    AND risk_score >= 70
ORDER BY risk_score DESC, created_at DESC;

-- ==============================================
-- 7. ROW LEVEL SECURITY (RLS) - Optional
-- ==============================================

-- Enable RLS on tables (for multi-tenant scenarios)
-- ALTER TABLE daily_sales ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE user_activity ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE fraud_signals ENABLE ROW LEVEL SECURITY;

-- Create policies as needed
-- Example: Allow service role full access
-- CREATE POLICY "Service role full access" ON daily_sales
--     FOR ALL
--     TO service_role
--     USING (true);

-- ==============================================
-- 8. GRANTS (for service role)
-- ==============================================

-- Grant all privileges to authenticated users (via service role)
GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres, anon, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO postgres, anon, authenticated, service_role;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO postgres, anon, authenticated, service_role;

-- ==============================================
-- 9. COMMENTS (Documentation)
-- ==============================================

COMMENT ON TABLE daily_sales IS 'Aggregated daily sales metrics from order and payment events';
COMMENT ON TABLE user_activity IS 'Hourly aggregation of user activity events';
COMMENT ON TABLE fraud_signals IS 'Detected fraud signals from payment pattern analysis';
COMMENT ON TABLE raw_events IS 'Raw events from Kafka topics for debugging and replay';

-- ==============================================
-- 10. STOCK SENTIMENT TABLE
-- ==============================================
CREATE TABLE IF NOT EXISTS stock_sentiment (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(10) NOT NULL,
    overall_score DECIMAL(4, 3) NOT NULL, -- -1.000 to 1.000
    overall_classification VARCHAR(20) NOT NULL,
    news_score DECIMAL(4, 3),
    reddit_score DECIMAL(4, 3),
    twitter_score DECIMAL(4, 3),
    trending_score DECIMAL(10, 2) DEFAULT 0,
    mention_count INTEGER DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_overall_score CHECK (overall_score >= -1 AND overall_score <= 1),
    CONSTRAINT valid_classification CHECK (overall_classification IN ('very_negative', 'negative', 'neutral', 'positive', 'very_positive'))
);

CREATE UNIQUE INDEX idx_stock_sentiment_symbol ON stock_sentiment(symbol);
CREATE INDEX idx_stock_sentiment_trending ON stock_sentiment(trending_score DESC);
CREATE INDEX idx_stock_sentiment_updated ON stock_sentiment(last_updated DESC);

-- ==============================================
-- 11. NEWS ARTICLES TABLE
-- ==============================================
CREATE TABLE IF NOT EXISTS news_articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(10) NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    url TEXT NOT NULL,
    source VARCHAR(255) NOT NULL,
    published_at TIMESTAMP WITH TIME ZONE NOT NULL,
    sentiment_score DECIMAL(4, 3) NOT NULL,
    sentiment_classification VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_news_sentiment CHECK (sentiment_score >= -1 AND sentiment_score <= 1)
);

CREATE INDEX idx_news_articles_symbol ON news_articles(symbol);
CREATE INDEX idx_news_articles_published ON news_articles(published_at DESC);
CREATE INDEX idx_news_articles_sentiment ON news_articles(sentiment_score);

-- ==============================================
-- 12. SOCIAL POSTS TABLE
-- ==============================================
CREATE TABLE IF NOT EXISTS social_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(10) NOT NULL,
    platform VARCHAR(20) NOT NULL, -- 'reddit', 'twitter'
    content TEXT NOT NULL,
    author VARCHAR(255),
    url TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    upvotes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    sentiment_score DECIMAL(4, 3) NOT NULL,
    sentiment_classification VARCHAR(20) NOT NULL,
    fetched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_platform CHECK (platform IN ('reddit', 'twitter')),
    CONSTRAINT valid_social_sentiment CHECK (sentiment_score >= -1 AND sentiment_score <= 1)
);

CREATE INDEX idx_social_posts_symbol ON social_posts(symbol);
CREATE INDEX idx_social_posts_platform ON social_posts(platform);
CREATE INDEX idx_social_posts_created ON social_posts(created_at DESC);

-- ==============================================
-- 13. PRICE ALERTS TABLE
-- ==============================================
CREATE TABLE IF NOT EXISTS price_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    symbol VARCHAR(10) NOT NULL,
    condition VARCHAR(20) NOT NULL, -- 'above', 'below', 'percent_up', 'percent_down'
    target_value DECIMAL(15, 4) NOT NULL,
    current_price DECIMAL(15, 4),
    status VARCHAR(20) DEFAULT 'active',
    message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    triggered_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT valid_alert_condition CHECK (condition IN ('above', 'below', 'percent_up', 'percent_down')),
    CONSTRAINT valid_alert_status CHECK (status IN ('active', 'triggered', 'expired', 'cancelled'))
);

CREATE INDEX idx_price_alerts_user ON price_alerts(user_id);
CREATE INDEX idx_price_alerts_symbol ON price_alerts(symbol);
CREATE INDEX idx_price_alerts_status ON price_alerts(status);
CREATE INDEX idx_price_alerts_active ON price_alerts(symbol, status) WHERE status = 'active';

-- ==============================================
-- 14. NOTIFICATIONS TABLE
-- ==============================================
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(30) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    symbol VARCHAR(10),
    data JSONB,
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_notification_type CHECK (type IN (
        'price_alert', 'price_change', 'volume_spike', 
        'sentiment_shift', 'signal_change', 'news_alert',
        'watchlist_update', 'system'
    ))
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_unread ON notifications(user_id, read) WHERE read = FALSE;
CREATE INDEX idx_notifications_created ON notifications(created_at DESC);

-- ==============================================
-- 15. WATCHLISTS TABLE
-- ==============================================
CREATE TABLE IF NOT EXISTS watchlists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL DEFAULT 'My Watchlist',
    symbols TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_user_watchlist_name UNIQUE(user_id, name)
);

CREATE INDEX idx_watchlists_user ON watchlists(user_id);

-- Trigger for watchlist updated_at
CREATE TRIGGER update_watchlists_updated_at
    BEFORE UPDATE ON watchlists
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ==============================================
-- 16. TECHNICAL ANALYSIS CACHE TABLE
-- ==============================================
CREATE TABLE IF NOT EXISTS technical_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(10) NOT NULL,
    timeframe VARCHAR(10) DEFAULT '1d',
    
    -- Moving Averages
    sma_20 DECIMAL(15, 4),
    sma_50 DECIMAL(15, 4),
    sma_200 DECIMAL(15, 4),
    ema_12 DECIMAL(15, 4),
    ema_26 DECIMAL(15, 4),
    
    -- MACD
    macd DECIMAL(15, 4),
    macd_signal DECIMAL(15, 4),
    macd_histogram DECIMAL(15, 4),
    
    -- RSI
    rsi_14 DECIMAL(5, 2),
    
    -- Bollinger Bands
    bb_upper DECIMAL(15, 4),
    bb_middle DECIMAL(15, 4),
    bb_lower DECIMAL(15, 4),
    
    -- Volatility
    atr_14 DECIMAL(15, 4),
    historical_volatility DECIMAL(8, 4),
    
    -- Signal
    signal VARCHAR(20),
    signal_confidence DECIMAL(4, 3),
    
    -- Support/Resistance
    support_level DECIMAL(15, 4),
    resistance_level DECIMAL(15, 4),
    
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_symbol_timeframe UNIQUE(symbol, timeframe)
);

CREATE INDEX idx_technical_analysis_symbol ON technical_analysis(symbol);
CREATE INDEX idx_technical_analysis_updated ON technical_analysis(last_updated DESC);

-- ==============================================
-- 17. USER ROLES TABLE (for admin features)
-- ==============================================
ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'user';
ALTER TABLE users ADD CONSTRAINT valid_user_role CHECK (role IN ('user', 'admin', 'moderator'));

CREATE INDEX idx_users_role ON users(role);

-- ==============================================
-- SCHEMA SETUP COMPLETE
-- ==============================================
