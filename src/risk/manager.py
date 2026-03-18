
from dataclasses import dataclass

@dataclass
class RiskProfile:
    max_position_pct: float = 0.15

class RiskManager:
    def __init__(self, config=None):
        self.config = config or RiskProfile()

risk_manager = RiskManager()
