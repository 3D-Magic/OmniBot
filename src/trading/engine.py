#!/usr/bin/env python3
"""
OMNIBOT v2.5 - Advanced Database Management
PostgreSQL with SQLite fallback, trade analytics
"""
from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, Boolean, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import os
import json
import sqlite3
import pandas as pd
from dataclasses import dataclass, asdict
import uuid


Base = declarative_base()


class TradeModel(Base):
    __tablename__ = 'trades'

    id = Column(String(36), primary_key=True)
    symbol = Column(String(10), index=True, nullable=False)
    side = Column(String(4), nullable=False)
    qty = Column(Integer, nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    entry_time = Column(DateTime, nullable=False, index=True)
    exit_time = Column(DateTime, nullable=True)
    pnl = Column(Float, default=0.0)
    pnl_pct = Column(Float, default=0.0)
    exit_reason = Column(String(50))
    market_regime = Column(String(20))
    strategy_id = Column(String(50))
    signal_confidence = Column(Float)
    ml_prediction = Column(Float)
    technical_score = Column(Float)
    sentiment_score = Column(Float)
    momentum_score = Column(Float)
    trade_metadata = Column(JSON)  # CRITICAL FIX: Changed from 'metadata' to 'trade_metadata'

    __table_args__ = (
        Index('idx_trades_symbol_time', 'symbol', 'entry_time'),
        Index('idx_trades_exit_time', 'exit_time'),
        Index('idx_trades_strategy', 'strategy_id'),
    )


class MarketDataModel(Base):
    __tablename__ = 'market_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), index=True, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float, nullable=False)
    volume = Column(Integer)
    vwap = Column(Float)
    regime = Column(String(20))

    __table_args__ = (
        Index('idx_market_symbol_time', 'symbol', 'timestamp'),
    )


class PerformanceModel(Base):
    __tablename__ = 'performance'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, index=True, nullable=False)
    total_equity = Column(Float)
    cash = Column(Float)
    open_positions = Column(Integer)
    daily_pnl = Column(Float)
    daily_return_pct = Column(Float)
    win_rate = Column(Float)
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)
    trades_count = Column(Integer)
    ml_accuracy = Column(Float)


@dataclass
class Trade:
    """Trade dataclass for type safety"""
    id: str
    symbol: str
    side: str
    qty: int
    entry_price: float
    entry_time: datetime
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    pnl: float = 0.0
    pnl_pct: float = 0.0
    exit_reason: str = ""
    market_regime: str = ""
    strategy_id: str = "v2.5"
    signal_confidence: float = 0.0
    ml_prediction: float = 0.0
    technical_score: float = 0.0
    sentiment_score: float = 0.0
    momentum_score: float = 0.0
    trade_metadata: Dict = None  # CRITICAL FIX: Changed from 'metadata' to 'trade_metadata'

    def __post_init__(self):
        if self.trade_metadata is None:
            self.trade_metadata = {}


class DatabaseManager:
    """Advanced database manager with analytics"""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.engine = create_engine(
            connection_string,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            echo=False
        )
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    @contextmanager
    def get_session(self) -> Session:
        """Context manager for database sessions"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    def save_trade(self, trade: Trade) -> None:
        """Save a trade to database"""
        with self.get_session() as session:
            model = TradeModel(**{
                k: v for k, v in asdict(trade).items()
                if k != 'trade_metadata' or v is not None  # CRITICAL FIX: Changed from 'metadata'
            })
            session.add(model)

    def update_trade_exit(self, trade_id: str, exit_price: float,
                          exit_time: datetime, pnl: float,
                          exit_reason: str) -> None:
        """Update trade with exit information"""
        with self.get_session() as session:
            trade = session.query(TradeModel).filter_by(id=trade_id).first()
            if trade:
                trade.exit_price = exit_price
                trade.exit_time = exit_time
                trade.pnl = pnl
                trade.pnl_pct = (pnl / (trade.entry_price * trade.qty)) * 100 if trade.entry_price else 0
                trade.exit_reason = exit_reason

    def get_trades(self, days: int = 2, symbol: Optional[str] = None,
                   strategy: Optional[str] = None,
                   min_pnl: Optional[float] = None) -> pd.DataFrame:
        """Get trades for analysis"""
        with self.get_session() as session:
            query = session.query(TradeModel)
            cutoff = datetime.now() - timedelta(days=days)
            query = query.filter(TradeModel.entry_time >= cutoff)

            if symbol:
                query = query.filter(TradeModel.symbol == symbol.upper())
            if strategy:
                query = query.filter(TradeModel.strategy_id == strategy)
            if min_pnl is not None:
                query = query.filter(TradeModel.pnl >= min_pnl)

            query = query.order_by(TradeModel.entry_time.desc())
            df = pd.read_sql(query.statement, session.bind)
            return df

    def get_trade_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Get comprehensive trade statistics"""
        with self.get_session() as session:
            cutoff = datetime.now() - timedelta(days=days)

            total_trades = session.query(TradeModel).filter(
                TradeModel.entry_time >= cutoff
            ).count()

            completed = session.query(TradeModel).filter(
                TradeModel.entry_time >= cutoff,
                TradeModel.exit_time.isnot(None)
            ).all()

            if not completed:
                return {
                    'period_days': days,
                    'total_trades': total_trades,
                    'completed_trades': 0,
                    'win_rate': 0.0,
                    'avg_pnl': 0.0,
                    'total_pnl': 0.0,
                    'sharpe': 0.0
                }

            wins = sum(1 for t in completed if t.pnl > 0)
            total_pnl = sum(t.pnl for t in completed)
            returns = [t.pnl_pct for t in completed if t.pnl_pct is not None]

            return {
                'period_days': days,
                'total_trades': total_trades,
                'completed_trades': len(completed),
                'win_rate': (wins / len(completed)) * 100 if completed else 0,
                'avg_pnl': total_pnl / len(completed) if completed else 0,
                'total_pnl': total_pnl,
                'avg_return_pct': sum(returns) / len(returns) if returns else 0,
                'sharpe': self._calculate_sharpe(returns) if returns else 0,
                'max_drawdown': self._calculate_max_drawdown(returns) if returns else 0,
                'best_trade': max(completed, key=lambda x: x.pnl).symbol if completed else None,
                'worst_trade': min(completed, key=lambda x: x.pnl).symbol if completed else None
            }

    def _calculate_sharpe(self, returns: List[float], risk_free: float = 0.0) -> float:
        """Calculate Sharpe ratio"""
        if len(returns) < 2:
            return 0.0
        import numpy as np
        excess = [r - risk_free for r in returns]
        return (np.mean(excess) / (np.std(excess) + 1e-9)) * np.sqrt(252)

    def _calculate_max_drawdown(self, returns: List[float]) -> float:
        """Calculate maximum drawdown"""
        if not returns:
            return 0.0
        cumulative = [1 + r / 100 for r in returns]
        running_max = [max(cumulative[:i + 1]) for i in range(len(cumulative))]
        drawdowns = [(c - m) / m for c, m in zip(cumulative, running_max)]
        return min(drawdowns) * 100 if drawdowns else 0


from config.settings import secure_settings
db_manager = DatabaseManager(secure_settings.database_url)
