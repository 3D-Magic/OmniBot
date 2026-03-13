#!/usr/bin/env python3
"""
OMNIBOT v2.5 - Configuration
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
from enum import Enum

class TradingMode(str, Enum):
    PAPER = "paper"
    LIVE = "live"
    BACKTEST = "backtest"

class SecureSettings(BaseSettings):
    """Settings loaded from environment"""

    alpaca_api_key_enc: str = Field(default="", env='ALPACA_API_KEY_ENC')
    alpaca_secret_key_enc: str = Field(default="", env='ALPACA_SECRET_KEY_ENC')
    newsapi_key_enc: str = Field(default="", env='NEWSAPI_KEY_ENC')
    polygon_key_enc: str = Field(default="", env='POLYGON_KEY_ENC')

    database_url: str = Field(default="sqlite:///omnibot.db", env='DATABASE_URL')
    redis_url: str = Field(default='redis://localhost:6379/0', env='REDIS_URL')
    trading_mode: TradingMode = Field(default=TradingMode.PAPER, env='TRADING_MODE')
    model_path: str = Field(default='./models', env='MODEL_PATH')
    data_path: str = Field(default='./data', env='DATA_PATH')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        use_enum_values = True

    @property
    def alpaca_api_key(self) -> str:
        return self.alpaca_api_key_enc if self.alpaca_api_key_enc else ""

    @property
    def alpaca_secret_key(self) -> str:
        return self.alpaca_secret_key_enc if self.alpaca_secret_key_enc else ""

    @property
    def newsapi_key(self) -> str:
        return self.newsapi_key_enc if self.newsapi_key_enc else ""

    @property
    def polygon_key(self) -> str:
        return self.polygon_key_enc if self.polygon_key_enc else ""

class TradingConfig(BaseSettings):
    """Trading parameters"""
    max_position_pct: float = 0.15
    symbols: List[str] = ['TQQQ', 'SOXL', 'TSLA', 'NVDA', 'AMD', 'AAPL', 
                          'MSFT', 'AMZN', 'GOOGL', 'META', 'SPY', 'QQQ', 'IWM']
    max_daily_trades: int = 50
    scan_interval: int = 10
    market_open_only: bool = True

secure_settings = SecureSettings()
trading_config = TradingConfig()
