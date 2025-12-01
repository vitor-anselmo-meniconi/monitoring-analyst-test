import pandas as pd
import numpy as np
from collections import deque

class TransactionMonitor:
	def __init__(self, window_size=60, threshold_sigma=3):
		"""
		Initializes the Transaction Monitor.
        
		:param window_size: Size of the rolling window (e.g., last 60 minutes) to calculate the moving average.
		:param threshold_sigma: Number of standard deviations above the mean to trigger an anomaly (Z-Score > 3).
		"""
		self.window_size = window_size
		self.threshold_sigma = threshold_sigma
        
		# Historical buffer to calculate baselines (Mean and Standard Deviation)
		# Using deque for efficient rolling window behavior
		self.history = {
			'failed': deque(maxlen=window_size),
			'denied': deque(maxlen=window_size),
			'reversed': deque(maxlen=window_size)
		}

	def ingest_data(self, minute_batch):
		"""
		Simulates the Endpoint receiving aggregated transaction data for a specific minute.
        
		Example input: {'timestamp': '10:00', 'failed': 2, 'denied': 5, 'reversed': 1, 'approved': 100}
        
		:param minute_batch: Dictionary containing aggregated counts for the minute.
		:return: Processing status and list of triggered alerts.
		"""
		alerts = []
        
		# Monitoring logic for each critical metric
		for metric in ['failed', 'denied', 'reversed']:
			value = minute_batch.get(metric, 0)
            
			# 1. Detect Anomaly
			if self._is_anomaly(metric, value):
				alert_msg = f"[ALERT 🚨] Anomaly detected in '{metric}': Current Value {value} (Expected Baseline: ~{self._get_mean(metric):.2f})"
				alerts.append(alert_msg)
				self._send_alert(alert_msg) # Simulation of sending to Slack/PagerDuty
            
			# 2. Update History (Continuous Learning)
			self.history[metric].append(value)
            
		return {"status": "processed", "alerts_triggered": alerts}

	def _is_anomaly(self, metric, value):
		"""
		Determines if a value is an anomaly using a Hybrid Model:
		- Static Threshold for 'failed' (Zero Tolerance).
		- Z-Score (Statistical) for 'denied' and 'reversed' (Adaptive).
		"""
        
		# Strategy A: Static Threshold for Critical Failures
		# Since failures should be near zero, any spike > 5 is an immediate critical incident.
		if metric == 'failed':
			return value > 5

		# Strategy B: Adaptive Statistical Scoring (Z-Score) for noisy metrics
		if len(self.history[metric]) < 10:
			return False # Insufficient data to infer pattern (Cold start period)
        
		mean = np.mean(self.history[metric])
		std = np.std(self.history[metric])
        
		# Safety check: avoid division by zero if standard deviation is 0
		if std == 0:
			# If historical variance is zero, any significant deviation is an anomaly
			return value > mean + 5 
            
		z_score = (value - mean) / std
		return z_score > self.threshold_sigma

	def _get_mean(self, metric):
		"""Helper to get the current moving average for a metric."""
		return np.mean(self.history[metric]) if self.history[metric] else 0

	def _send_alert(self, message):
		"""Mock function to simulate external alert dispatch (e.g., webhook)."""
		print(message)

# --- Execution Simulation (Test) ---
if __name__ == "__main__":
	monitor = TransactionMonitor()
    
	print("Training model with normal data...")
	# Simulating 60 minutes of normal traffic to "train" the moving average
	for _ in range(60):
		monitor.ingest_data({'failed': 0, 'denied': 5, 'reversed': 1})
        
	# Injecting an ANOMALY (Simulating a spike in failures)
	print("\n--- Injecting Anomaly (Simulation) ---")
	# This input represents a critical failure spike (Failed=15)
	response = monitor.ingest_data({'failed': 15, 'denied': 8, 'reversed': 2})
    
	print(f"\nResponse from Monitor: {response}")

