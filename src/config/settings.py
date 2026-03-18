#!/usr/bin/env python3
"""
OMNIBOT v2.5.1 - Configuration with Asia & Forex Markets
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Dict
from enum import Enum


class TradingMode(str, Enum):
    PAPER = "paper"
    LIVE = "live"
    BACKTEST = "backtest"


class SecureSettings(BaseSettings):
    """Settings loaded from .env file"""

    alpaca_api_key_enc: str = Field(default="", env='ALPACA_API_KEY_ENC')
    alpaca_secret_key_enc: str = Field(default="", env='ALPACA_SECRET_KEY_ENC')
    newsapi_key_enc: str = Field(default="", env='NEWSAPI_KEY_ENC')
    polygon_key_enc: str = Field(default="", env='POLYGON_KEY_ENC')

    database_url: str = Field(default="sqlite:///omnibot.db", env='DATABASE_URL')
    redis_url: str = Field(default='redis://localhost:6379/0', env='REDIS_URL')
    trading_mode: TradingMode = Field(default=TradingMode.PAPER, env='TRADING_MODE')

    model_path: str = Field(default='/home/biqu/omnibot/models', env='MODEL_PATH')
    data_path: str = Field(default='/home/biqu/omnibot/data', env='DATA_PATH')

    class Config:
        env_file = '/home/biqu/omnibot/.env'
        env_file_encoding = 'utf-8'
        use_enum_values = True

    @property
    def alpaca_api_key(self) -> str:
        return self.alpaca_api_key_enc if self.alpaca_api_key_enc else ""

    @property
    def alpaca_secret_key(self) -> str:
        return self.alpaca_secret_key_enc if self.alpaca_secret_key_enc else ""


class TradingConfig(BaseSettings):
    """Trading parameters with multi-market support"""

    # US Market
    us_symbols: List[str] = [
        'TQQQ', 'SOXL', 'TSLA', 'NVDA', 'AMD', 'AAPL',
        'MSFT', 'AMZN', 'GOOGL', 'META', 'SPY', 'QQQ', 'IWM'
    ]

    # Asia Markets
    japan_symbols: List[str] = [
        '7203.T', '6758.T', '9984.T', '6861.T', '7974.T'
    ]
    hongkong_symbols: List[str] = [
        '0700.HK', '3690.HK', '9988.HK', '2318.HK', '1299.HK'
    ]
    singapore_symbols: List[str] = [
        'D05.SI', 'O39.SI', 'U11.SI', 'Z74.SI'
    ]

    # Forex Pairs
    forex_symbols: List[str] = [
        'EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X',
        'USDCAD=X', 'USDCHF=X', 'NZDUSD=X', 'EURGBP=X'
    ]

    # Market enable flags
    enable_us: bool = True
    enable_japan: bool = True
    enable_hongkong: bool = True
    enable_singapore: bool = False  # Disabled by default
    enable_forex: bool = True

    # Trading parameters
    max_position_pct: float = 0.15
    max_daily_trades: int = 50
    scan_interval: int = 10
    market_open_only: bool = True

    @property
    def symbols(self) -> List[str]:
        """Get all enabled symbols"""
        all_symbols = []
        if self.enable_us:
            all_symbols.extend(self.us_symbols)
        if self.enable_japan:
            all_symbols.extend(self.japan_symbols)
        if self.enable_hongkong:
            all_symbols.extend(self.hongkong_symbols)
        if self.enable_singapore:
            all_symbols.extend(self.singapore_symbols)
        if self.enable_forex:
            all_symbols.extend(self.forex_symbols)
        return all_symbols


secure_settings = SecureSettings()
trading_config = TradingConfig()
