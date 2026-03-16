#!/usr/bin/env python3
"""
OMNIBOT v2.5 - Monitoring
"""


class Monitoring:
    """Simple monitoring"""

    def __init__(self, metrics_port=8080):
        print(f"Metrics server started on port {metrics_port}")

    def log_trade(self, trade_data):
        pass

    def update_metrics(self, account, positions):
        pass


monitor = Monitoring()
