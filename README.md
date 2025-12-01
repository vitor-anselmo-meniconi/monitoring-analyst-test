# CloudWalk Monitoring Challenge: Anomaly Detection & Real-Time Alerting

> "Where there is data smoke, there is business fire." — Thomas Redman

## Introduction

This repository hosts the solution for the Monitoring Analyst Technical Assessment. The project focuses on analyzing historical checkout data to identify service availability incidents and engineering a real-time monitoring system capable of distinguishing between organic traffic fluctuations and critical system failures.

## Project Deliverables

Per the challenge requirements, here are the detailed documents regarding the execution:

| Challenge Part | Description | Document |
|---|---|---|
| Part 1 | Analysis of hypothetical checkout data | [View Analysis PDF](./docs/Part1_Analysis.pdf) |
| Part 2 | Real-world monitoring solution & code | [View Solution PDF](./docs/Part2_Solution.pdf) |

## Project Structure

```
cw-monitoring-challenge/
├── README.md               # Main documentation: Analysis results, System Architecture, and Usage
├── assets/                 # Visualization assets and charts used in the reports
│   ├── checkout_1_analysis.png
│   ├── checkout_2_analysis.png
│   ├── transactions.png
│   └── realtime_dashboard.png
├── data/                   # Raw input datasets (CSVs)
│   ├── checkout_1.csv
│   ├── checkout_2.csv
│   ├── transactions.csv
│   └── transactions_auth_codes.csv
├── docs/                   # Official deliverables and detailed reports (PDFs)
│   ├── Part1_Analysis.pdf
│   └── Part2_Solution.pdf
└── src/                    # Source code for the monitoring solution
    ├── aggregation.sql     # SQL query for real-time data aggregation
    ├── dashboard.py        # Script to generate the Real-Time Operations Dashboard
    └── monitor.py          # Core alerting system (Endpoint simulation + Hybrid Model)
```

## Part 1: Data Analysis & Conclusions

The following analysis details the identification of two critical availability incidents based on the sharp deviation between the actual transactional volume and the historical baseline (`avg_last_week`).

### Methodology

By cross-referencing the `today` column (current real-time data) against the `avg_last_week` column (expected baseline behavior), I identified two distinct and critical incidents.

### Scenario A: Checkout 1 — Severe Service Degradation

**The Anomaly:** Between 08:00 and 09:00, there was a drastic drop in sales volume. The red-shaded area highlights the trough where performance dropped nearly 100% relative to expectations.

- At 08:00, sales hit **0** (expected average was ~8.7)
- At 09:00, sales were **2** (expected average was ~20)

**The Rebound Effect (Catch-up):** At 10:00, sales surged to 55, significantly surpassing the historical average of 29. Here, the red peak overtakes the green baseline, confirming the system recovery theory.

**Conclusion:** This indicates a system failure or severe latency during the morning ramp-up period. The spike at 10:00 suggests that the system came back online and processed a backlog of queued transactions.

### Scenario B: Checkout 2 — Total Unavailability (Hard Down)

**The Anomaly:** Between 15:00 and 17:00, sales volume flatlined to exactly zero.

**Context:** This represents a peak business window. The historical baseline (`avg_last_week`) indicates an expected volume of 22 to 28 sales per hour during this period.

**Visual Evidence:** The gap between the red line (Actual) and green line (Expected) visually represents the direct financial loss incurred during the outage.

**Conclusion:** Unlike Checkout 1, this scenario depicts a Total Outage. No processing occurred for three consecutive hours, resulting in irreversible revenue loss with no immediate recovery.

## Part 2: Technical Solution (Real-Time Monitoring)

This system was engineered to monitor transaction health in real-time and facilitate rapid incident response. Utilizing Python and SQL, the solution analyzes data at minute-level granularity through a hybrid strategy.

### 1. Exploratory Data Analysis (Establishing Baselines)

Prior to implementation, I analyzed the provided datasets to understand the baseline behavior of the system:

- **Approved Transactions:** Avg ~116/min (Normal Flow)
- **Denied Transactions:** Avg ~7/min (Peaks reach 58 → Anomaly)
- **Failed Transactions:** Avg ~0.06/min (Peaks reach 10 → Critical Anomaly)

### 2. The Hybrid Detection Model

Based on the metrics above, a hybrid approach was chosen because a single detection technique is insufficient to cover all scenarios efficiently.

#### Strategy A: Static Thresholds (Rule-Based)

- **Target:** Failed transactions
- **Rule:** `IF failed_count > 5 THEN Trigger Critical Alert`
- **Why:** Ensures zero tolerance for system errors

#### Strategy B: Adaptive Statistical Scoring (Z-Score)

- **Target:** Denied transactions
- **Rule:** `IF Z-Score > 3 THEN Trigger Warning`
- **Why:** Dynamically adapts to organic growth preventing false positives

### 3. SQL Query for Aggregation

The following query transforms raw logs into the minute-by-minute format consumed by the monitoring system.

```sql
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
```

### 4. Real-Time Dashboard View

Below is the Operational Dashboard generated by the `dashboard.py` script. It visualizes the processed metrics in real-time buckets.

- **Failed (Red):** Note that the red line rarely rises. Any spike exceeding 2-3 events is immediately visible.
- **Denied (Orange):** The line exhibits naturally noisier behavior, necessitating a higher alert threshold (Z-Score) to avoid false positives.

## Conclusion

The solution implements a hybrid, automated monitoring strategy, combining Z-Score analysis to identify statistical traffic deviations and Static Thresholds (Hard Limits) to instantly alert on critical failures. The system operates autonomously through the `monitor.py` script, eliminating human error in detection, and presents data via a segmented dashboard. This empowers the NOC team to rapidly distinguish between technical incidents, potential fraud attempts, and operational issues.

## How to Run This Project

```bash
# Install dependencies
pip install pandas matplotlib numpy

# Run the Real-Time Dashboard Generator
python src/dashboard.py

# Run the Monitoring Alert System (Simulation)
python src/monitor.py
```
