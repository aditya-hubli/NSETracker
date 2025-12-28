-- ==============================================
-- SEED DATA FOR TESTING
-- ==============================================

-- Insert sample daily sales data
INSERT INTO daily_sales (date, total_orders, total_revenue, total_items_sold, average_order_value, completed_payments, failed_payments, cancelled_orders)
VALUES
    (CURRENT_DATE - INTERVAL '7 days', 45, 3250.50, 120, 72.23, 43, 2, 0),
    (CURRENT_DATE - INTERVAL '6 days', 52, 4100.75, 145, 78.86, 50, 2, 0),
    (CURRENT_DATE - INTERVAL '5 days', 38, 2890.25, 98, 76.06, 36, 2, 0),
    (CURRENT_DATE - INTERVAL '4 days', 61, 5230.00, 178, 85.74, 59, 2, 0),
    (CURRENT_DATE - INTERVAL '3 days', 48, 3675.50, 132, 76.57, 46, 2, 0),
    (CURRENT_DATE - INTERVAL '2 days', 55, 4520.25, 156, 82.19, 53, 2, 0),
    (CURRENT_DATE - INTERVAL '1 day', 42, 3180.00, 115, 75.71, 40, 2, 0)
ON CONFLICT (date) DO NOTHING;

-- Insert sample user activity data
INSERT INTO user_activity (user_id, hour_bucket, event_count, event_types, last_activity, first_activity)
VALUES
    ('user_001', DATE_TRUNC('hour', NOW() - INTERVAL '2 hours'), 15, '["user_created", "user_updated"]'::jsonb, NOW() - INTERVAL '2 hours', NOW() - INTERVAL '2 hours'),
    ('user_002', DATE_TRUNC('hour', NOW() - INTERVAL '1 hour'), 8, '["user_created"]'::jsonb, NOW() - INTERVAL '1 hour', NOW() - INTERVAL '1 hour'),
    ('user_003', DATE_TRUNC('hour', NOW()), 23, '["user_updated", "user_created"]'::jsonb, NOW(), NOW() - INTERVAL '30 minutes')
ON CONFLICT (user_id, hour_bucket) DO NOTHING;

-- Insert sample fraud signals
INSERT INTO fraud_signals (window_start, window_end, user_id, payment_id, signal_type, failed_payment_count, total_amount, risk_score, metadata)
VALUES
    (NOW() - INTERVAL '30 minutes', NOW() - INTERVAL '15 minutes', 'user_suspicious_001', 'pay_12345', 'multiple_failures', 5, 2500.00, 85.5, '{"ip_address": "192.168.1.1", "location": "unknown"}'::jsonb),
    (NOW() - INTERVAL '1 hour', NOW() - INTERVAL '45 minutes', 'user_suspicious_002', 'pay_67890', 'high_frequency', 3, 1800.00, 72.3, '{"transaction_count": 10, "time_span_minutes": 15}'::jsonb)
ON CONFLICT DO NOTHING;

-- ==============================================
-- SEED DATA COMPLETE
-- ==============================================
