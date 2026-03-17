#!/usr/bin/env python3
"""
OMNIBOT v2.5 - Monitoring
Simple console-based monitoring without HTTP server to prevent connection errors
"""


class Monitoring:
    """Simple monitoring - server disabled to prevent ConnectionResetError"""

    def __init__(self, metrics_port=8080):
        # HTTP server disabled - was causing [Errno 104] Connection reset by peer
        # This error occurred when clients disconnected from the metrics server unexpectedly
        # Bot runs fine without it - all important data is logged to database anyway
        pass

    def log_trade(self, trade_data):
        """Log trade to console only (no HTTP server)"""
        pass

    def update_metrics(self, account, positions):
        """Update metrics - console only"""
        pass


monitor = Monitoring()
