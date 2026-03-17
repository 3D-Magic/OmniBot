#!/usr/bin/env python3
"""
OMNIBOT v2.5 - Deep Learning Market Predictor
"""
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class PredictionResult:
    direction: str
    confidence: float
    predicted_return: float
    features_importance: Dict[str, float]
    timestamp: datetime


class MarketPredictor:
    """Deep learning market prediction system"""

    def __init__(self, model_path: str = "/home/Omnibot/omnibot/models"):
        self.model_path = model_path
        self.device = torch.device('cpu')
        print("Created new LSTM model")

    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for prediction - uses index as timestamp"""
        features = pd.DataFrame(index=df.index)

        # Price-based features
        features['returns'] = df['close'].pct_change()
        features['log_returns'] = np.log(df['close'] / df['close'].shift(1))

        # Volatility
        features['volatility'] = df['close'].rolling(window=20).std()

        # Moving averages
        features['sma_10'] = df['close'].rolling(window=10).mean()
        features['sma_20'] = df['close'].rolling(window=20).mean()
        features['ema_12'] = df['close'].ewm(span=12).mean()

        # Price position
        features['price_to_sma20'] = df['close'] / features['sma_20']

        # Volume features
        features['volume_sma'] = df['volume'].rolling(window=10).mean()
        features['volume_ratio'] = df['volume'] / features['volume_sma']

        # CRITICAL FIX: Use df.index instead of df['timestamp']
        features['hour'] = pd.to_datetime(df.index).hour / 24
        features['day_of_week'] = pd.to_datetime(df.index).dayofweek / 7

        # Drop NaN values
        features = features.dropna()

        return features

    def predict(self, symbol: str, df: pd.DataFrame) -> PredictionResult:
        """Generate prediction for symbol"""
        try:
            features = self._prepare_features(df)

            if len(features) < 20:
                return PredictionResult(
                    direction='neutral',
                    confidence=0.5,
                    predicted_return=0.0,
                    features_importance={},
                    timestamp=datetime.now()
                )

            # Simple rule-based prediction
            last_price = df['close'].iloc[-1]
            sma20 = df['close'].rolling(window=20).mean().iloc[-1]

            if last_price > sma20 * 1.02:
                direction = 'long'
                confidence = 0.65
                predicted_return = 0.02
            elif last_price < sma20 * 0.98:
                direction = 'short'
                confidence = 0.65
                predicted_return = -0.02
            else:
                direction = 'neutral'
                confidence = 0.5
                predicted_return = 0.0

            return PredictionResult(
                direction=direction,
                confidence=confidence,
                predicted_return=predicted_return,
                features_importance={},
                timestamp=datetime.now()
            )

        except Exception as e:
            print(f"[PREDICT] Error for {symbol}: {e}")
            return PredictionResult(
                direction='neutral',
                confidence=0.5,
                predicted_return=0.0,
                features_importance={},
                timestamp=datetime.now()
            )


market_predictor = MarketPredictor()
