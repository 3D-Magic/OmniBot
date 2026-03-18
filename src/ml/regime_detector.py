
from enum import Enum
from dataclasses import dataclass

class MarketRegime(Enum):
    UNKNOWN = "unknown"

@dataclass
class RegimeMetrics:
    regime: MarketRegime

class RegimeDetector:
    def detect(self, prices, volume=None):
        return RegimeMetrics(MarketRegime.UNKNOWN)

regime_detector = RegimeDetector()
