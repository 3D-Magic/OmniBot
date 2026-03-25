from enum import Enum
from typing import Dict, List, Optional

class TradingMode(Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    HFT = "hft"
    SENTINEL = "sentinel"

class Settings:
    VERSION = "v2.6.1 Sentinel"
    TRADING_MODE = TradingMode.AGGRESSIVE
    MAX_CONCURRENT_POSITIONS = 10
    MAX_DAILY_LOSS = 0.10
    AUTO_UPDATE_ENABLED = True
    UPDATE_ON_WEEKEND = True
    UPDATE_CHECK_INTERVAL_HOURS = 24
    AUTO_CLOSE_ENABLED = True
    AUTO_CLOSE_TIME = "16:00"
    AUTO_CLOSE_WEEKEND = True
    DASHBOARD_PORT = 8081
    GITHUB_REPO = "3D-Magic/OmniBot-Testing"
    PAPER_TRADING = False

    @classmethod
    def set_trading_mode(cls, mode: str):
        mode_map = {
            "conservative": TradingMode.CONSERVATIVE,
            "moderate": TradingMode.MODERATE,
            "aggressive": TradingMode.AGGRESSIVE,
            "hft": TradingMode.HFT,
            "sentinel": TradingMode.SENTINEL
        }
        cls.TRADING_MODE = mode_map.get(mode.lower(), TradingMode.AGGRESSIVE)
