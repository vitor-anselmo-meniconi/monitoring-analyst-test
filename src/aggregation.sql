/*
 * Aggregation Query for Monitoring Dashboard
 * Groups raw transaction logs by minute and status to feed the alerting system.
 */

SELECT
    DATE_TRUNC('minute', created_at) AS time_bucket,
    
    -- Core monitoring metrics
    COUNT(*) FILTER (WHERE status = 'approved') AS approved_count,
    COUNT(*) FILTER (WHERE status = 'denied') AS denied_count,
    COUNT(*) FILTER (WHERE status = 'failed') AS failed_count,
    COUNT(*) FILTER (WHERE status IN ('reversed', 'backend_reversed')) AS reversed_count,
    
    -- Performance Metrics (Optional context)
    AVG(duration_ms) as avg_latency
FROM
    transactions_log
WHERE
    created_at >= NOW() - INTERVAL '1 hour' -- Real-time sliding window
GROUP BY
    1
ORDER BY
    1 DESC;
