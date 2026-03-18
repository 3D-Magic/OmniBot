#!/usr/bin/env python3
"""
OMNIBOT v2.5.1 - Data Client
"""
import pandas as pd
import yfinance as yf


class HybridDataClient:
    def __init__(self):
        self.has_credentials = True

    def get_bars(self, symbol: str, limit: int = 100, timeframe: str = '5m'):
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
