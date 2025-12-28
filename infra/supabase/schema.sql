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
-- SCHEMA SETUP COMPLETE
-- ==============================================
