"""
OMNIBOT Strategies Engine
Manages multiple trading strategies
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime

from config.settings import STRATEGIES

logger = logging.getLogger(__name__)


class Strategy:
    """Base strategy class"""

    def __init__(self, name: str, weight: float = 1.0):
        self.name = name
        self.weight = weight
        self.enabled = True
        self.signals: List[Dict] = []

    def generate_signal(self, data: pd.DataFrame) -> Optional[str]:
        """Generate trading signal - override in subclass"""
        return None

    def get_confidence(self) -> float:
        """Get strategy confidence score"""
        return 0.5


class MomentumStrategy(Strategy):
    """Momentum-based strategy"""

    def __init__(self, lookback: int = 20):
        super().__init__("momentum", 0.25)
        self.lookback = lookback

    def generate_signal(self, data: pd.DataFrame) -> Optional[str]:
        if len(data) < self.lookback:
            return None

        # Calculate momentum
        current_price = data['Close'].iloc[-1]
        past_price = data['Close'].iloc[-self.lookback]
        momentum = (current_price - past_price) / past_price * 100

        if momentum > 5:
            return "buy"
        elif momentum < -5:
            return "sell"

        return None

    def get_confidence(self) -> float:
        return 0.7


class MeanReversionStrategy(Strategy):
    """Mean reversion strategy"""

    def __init__(self, z_threshold: float = 2.0):
        super().__init__("mean_reversion", 0.25)
        self.z_threshold = z_threshold

    def generate_signal(self, data: pd.DataFrame) -> Optional[str]:
        if len(data) < 20:
            return None

        # Calculate z-score
        mean = data['Close'].mean()
        std = data['Close'].std()
        current = data['Close'].iloc[-1]
        z_score = (current - mean) / std if std != 0 else 0

        if z_score < -self.z_threshold:
            return "buy"  # Oversold
        elif z_score > self.z_threshold:
            return "sell"  # Overbought

        return None

    def get_confidence(self) -> float:
        return 0.6


class BreakoutStrategy(Strategy):
    """Breakout strategy"""

    def __init__(self, atr_period: int = 14):
        super().__init__("breakout", 0.25)
        self.atr_period = atr_period

    def generate_signal(self, data: pd.DataFrame) -> Optional[str]:
        if len(data) < self.atr_period + 5:
            return None

        # Calculate ATR
        high_low = data['High'] - data['Low']
        high_close = np.abs(data['High'] - data['Close'].shift())
        low_close = np.abs(data['Low'] - data['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        atr = true_range.rolling(self.atr_period).mean().iloc[-1]

        current_price = data['Close'].iloc[-1]
        prev_high = data['High'].iloc[-5:-1].max()
        prev_low = data['Low'].iloc[-5:-1].min()

        if current_price > prev_high + atr * 0.5:
            return "buy"
        elif current_price < prev_low - atr * 0.5:
            return "sell"

        return None

    def get_confidence(self) -> float:
        return 0.65


class MLEnsembleStrategy(Strategy):
    """Machine Learning ensemble strategy using scikit-learn"""

    def __init__(self):
        super().__init__("ml_ensemble", 0.25)
        self.model = None
        self.is_trained = False

    def _prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """Prepare features for ML model"""
        features = []

        # Technical indicators
        data['SMA_20'] = data['Close'].rolling(20).mean()
        data['SMA_50'] = data['Close'].rolling(50).mean()
        data['RSI'] = self._calculate_rsi(data['Close'], 14)
        data['MACD'] = self._calculate_macd(data['Close'])

        # Feature vector
        latest = data.iloc[-1]
        features = [
            latest['Close'] / latest['SMA_20'] - 1 if latest['SMA_20'] != 0 else 0,
            latest['Close'] / latest['SMA_50'] - 1 if latest['SMA_50'] != 0 else 0,
            latest['RSI'] / 100,
            latest['MACD'],
            data['Volume'].iloc[-1] / data['Volume'].rolling(20).mean().iloc[-1] if data['Volume'].rolling(20).mean().iloc[-1] != 0 else 1
        ]

        return np.array(features).reshape(1, -1)

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_macd(self, prices: pd.Series) -> float:
        """Calculate MACD"""
        ema_12 = prices.ewm(span=12).mean().iloc[-1]
        ema_26 = prices.ewm(span=26).mean().iloc[-1]
        return ema_12 - ema_26

    def generate_signal(self, data: pd.DataFrame) -> Optional[str]:
        if len(data) < 50:
            return None

        try:
            from sklearn.ensemble import RandomForestClassifier

            # Simple rule-based for now (can be trained)
            features = self._prepare_features(data)

            # Trend following logic
            sma_20 = data['Close'].rolling(20).mean().iloc[-1]
            sma_50 = data['Close'].rolling(50).mean().iloc[-1]

            if sma_20 > sma_50 * 1.02:
                return "buy"
            elif sma_20 < sma_50 * 0.98:
                return "sell"

        except ImportError:
            logger.warning("scikit-learn not available, using fallback")
            return None

        return None

    def get_confidence(self) -> float:
        return 0.75 if self.is_trained else 0.5


class StrategiesEngine:
    """Manages all trading strategies"""

    def __init__(self):
        self.strategies: Dict[str, Strategy] = {}
        self._init_strategies()
        logger.info("StrategiesEngine initialized")

    def _init_strategies(self):
        """Initialize all strategies from config"""
        config = STRATEGIES

        if config.get('momentum', {}).get('enabled', True):
            self.strategies['momentum'] = MomentumStrategy(
                lookback=config['momentum'].get('lookback', 20)
            )

        if config.get('mean_reversion', {}).get('enabled', True):
            self.strategies['mean_reversion'] = MeanReversionStrategy(
                z_threshold=config['mean_reversion'].get('z_threshold', 2.0)
            )

        if config.get('breakout', {}).get('enabled', True):
            self.strategies['breakout'] = BreakoutStrategy(
                atr_period=config['breakout'].get('atr_period', 14)
            )

        if config.get('ml_ensemble', {}).get('enabled', True):
            self.strategies['ml_ensemble'] = MLEnsembleStrategy()

    def generate_consensus(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate consensus signal from all strategies"""
        signals = {}
        total_weight = 0
        weighted_score = 0

        for name, strategy in self.strategies.items():
            if not strategy.enabled:
                continue

            signal = strategy.generate_signal(data)
            weight = strategy.weight
            confidence = strategy.get_confidence()

            signals[name] = {
                'signal': signal,
                'weight': weight,
                'confidence': confidence
            }

            # Calculate weighted score
            if signal == "buy":
                weighted_score += weight * confidence
            elif signal == "sell":
                weighted_score -= weight * confidence

            total_weight += weight

        # Normalize
        if total_weight > 0:
            consensus_score = weighted_score / total_weight
        else:
            consensus_score = 0

        # Determine action
        if consensus_score > 0.3:
            consensus = "buy"
        elif consensus_score < -0.3:
            consensus = "sell"
        else:
            consensus = "hold"

        return {
            'consensus': consensus,
            'score': consensus_score,
            'individual_signals': signals,
            'timestamp': datetime.now().isoformat()
        }

    def get_strategy_status(self) -> Dict[str, Any]:
        """Get status of all strategies"""
        return {
            name: {
                'enabled': s.enabled,
                'weight': s.weight,
                'confidence': s.get_confidence()
            }
            for name, s in self.strategies.items()
        }


def create_strategies_engine() -> StrategiesEngine:
    """Factory function"""
    return StrategiesEngine()
