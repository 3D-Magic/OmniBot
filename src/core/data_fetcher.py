"""
OMNIBOT Data Fetcher
Handles market data retrieval and caching
"""

import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

import yfinance as yf
import pandas as pd

from config.settings import DATA_SOURCES, CACHE_DIR

logger = logging.getLogger(__name__)


class DataFetcher:
    """Fetches and caches market data"""

    def __init__(self):
        self.primary_source = DATA_SOURCES.get('primary', 'yfinance')
        self.cache_enabled = DATA_SOURCES.get('cache_enabled', True)
        self.cache_duration = DATA_SOURCES.get('cache_duration_minutes', 15)
        self.cache_dir = Path(CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self._cache: Dict[str, Any] = {}
        self._cache_time: Dict[str, datetime] = {}

        logger.info(f"DataFetcher initialized (cache: {self.cache_enabled})")

    def _get_cache_key(self, symbol: str, data_type: str) -> str:
        """Generate cache key"""
        return f"{symbol}_{data_type}"

    def _is_cache_valid(self, key: str) -> bool:
        """Check if cache entry is still valid"""
        if key not in self._cache_time:
            return False

        age = datetime.now() - self._cache_time[key]
        return age < timedelta(minutes=self.cache_duration)

    def _load_from_cache(self, key: str) -> Optional[Any]:
        """Load data from memory cache"""
        if not self.cache_enabled:
            return None

        if key in self._cache and self._is_cache_valid(key):
            return self._cache[key]

        return None

    def _save_to_cache(self, key: str, data: Any):
        """Save data to memory cache"""
        if not self.cache_enabled:
            return

        self._cache[key] = data
        self._cache_time[key] = datetime.now()

    def get_stock_data(self, symbol: str, period: str = "1d", 
                       interval: str = "1m") -> Optional[pd.DataFrame]:
        """Fetch stock price data"""
        cache_key = self._get_cache_key(symbol, f"{period}_{interval}")

        # Check cache
        cached = self._load_from_cache(cache_key)
        if cached is not None:
            return cached

        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)

            if data.empty:
                logger.warning(f"No data returned for {symbol}")
                return None

            # Save to cache
            self._save_to_cache(cache_key, data)

            logger.debug(f"Fetched {len(data)} bars for {symbol}")
            return data

        except Exception as e:
            logger.error(f"Failed to fetch data for {symbol}: {e}")
            return None

    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol"""
        data = self.get_stock_data(symbol, period="1d", interval="1m")

        if data is not None and not data.empty:
            return float(data['Close'].iloc[-1])

        return None

    def get_multiple_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Get current prices for multiple symbols"""
        prices = {}

        for symbol in symbols:
            price = self.get_current_price(symbol)
            if price is not None:
                prices[symbol] = price
            time.sleep(0.1)  # Rate limiting

        return prices

    def get_info(self, symbol: str) -> Optional[Dict]:
        """Get stock info"""
        cache_key = self._get_cache_key(symbol, "info")

        cached = self._load_from_cache(cache_key)
        if cached is not None:
            return cached

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            self._save_to_cache(cache_key, info)
            return info

        except Exception as e:
            logger.error(f"Failed to get info for {symbol}: {e}")
            return None

    def clear_cache(self):
        """Clear all cached data"""
        self._cache.clear()
        self._cache_time.clear()
        logger.info("Cache cleared")


def create_fetcher() -> DataFetcher:
    """Factory function to create data fetcher"""
    return DataFetcher()
