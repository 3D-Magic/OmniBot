#!/usr/bin/env python3
"""
OMNIBOT v2.5 - Data Client
Uses Yahoo Finance (free) instead of Alpaca paid data
"""
import pandas as pd
from typing import Optional
import yfinance as yf
from datetime import datetime, timedelta


class HybridDataClient:
    """Data client using Yahoo Finance (free)"""

    def __init__(self):
        self.has_credentials = True  # yfinance doesn't need credentials

    def get_bars(self, symbol: str, limit: int = 100, timeframe: str = '1Min'):
        """Get price bars from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)

            # Get last 2 days of 5-minute data (free tier)
            df = ticker.history(period="2d", interval="5m")

            if df is not None and not df.empty:
                # Reset index to make Datetime a column
                df = df.reset_index()

                # Rename columns to lowercase
                df = df.rename(columns={
                    'Datetime': 'timestamp',
                    'Open': 'open',
                    'High': 'high',
                    'Low': 'low',
                    'Close': 'close',
                    'Volume': 'volume'
                })

                # Keep only needed columns
                df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]

                # Set timestamp as index
                df.set_index('timestamp', inplace=True)

                print(f"[DATA] Fetched {len(df)} bars for {symbol} from Yahoo")
                return df
            else:
                print(f"[DATA] No data returned for {symbol}")
                return None

        except Exception as e:
            print(f"[DATA] Error fetching {symbol}: {e}")
            return None


data_client = HybridDataClient()
