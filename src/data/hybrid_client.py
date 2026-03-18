#!/usr/bin/env python3
"""
OMNIBOT v3.0 - Data Client (Legacy compatibility)
"""
import pandas as pd
import yfinance as yf


class HybridDataClient:
    """Data client using Yahoo Finance"""

    def __init__(self):
        self.has_credentials = True

    def get_bars(self, symbol: str, limit: int = 100, timeframe: str = '5m'):
        """Get price bars from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="3d", interval="5m")
            if df.empty:
                return None
            df = df.rename(columns={
                'Open': 'open', 'High': 'high', 'Low': 'low',
                'Close': 'close', 'Volume': 'volume'
            })
            return df
        except Exception as e:
            return None


data_client = HybridDataClient()
