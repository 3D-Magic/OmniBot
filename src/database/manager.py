#!/usr/bin/env python3
"""
OMNIBOT v2.5 - Database Management
Copyright (c) 2026 3D-Magic

LICENSE: Personal Use Only
- Free for individual personal trading
- NO sale, NO modifications, NO redistribution
"""

from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
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
    trade_metadata = Column(JSON)

    __table_args__ = (
        Index('idx_trades_symbol_time', 'symbol', 'entry_time'),
        Index('idx_trades_exit_time', 'exit_time'),
        Index('idx_trades_strategy', 'strategy_id'),
    )

@dataclass
class Trade:
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
    trade_metadata: Dict = None

    def __post_init__(self):
        if self.trade_metadata is None:
            self.trade_metadata = {}

class DatabaseManager:
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
        with self.get_session() as session:
            model = TradeModel(**{
                k: v for k, v in asdict(trade).items()
                if k != 'trade_metadata' or v is not None
            })
            session.add(model)

    def get_trades(self, days: int = 2, symbol: Optional[str] = None) -> pd.DataFrame:
        with self.get_session() as session:
            query = session.query(TradeModel)
            cutoff = datetime.now() - timedelta(days=days)
            query = query.filter(TradeModel.entry_time >= cutoff)
            if symbol:
                query = query.filter(TradeModel.symbol == symbol.upper())
            query = query.order_by(TradeModel.entry_time.desc())
            return pd.read_sql(query.statement, session.bind)

    def get_trade_statistics(self, days: int = 7) -> Dict[str, Any]:
        with self.get_session() as session:
            cutoff = datetime.now() - timedelta(days=days)
            completed = session.query(TradeModel).filter(
                TradeModel.entry_time >= cutoff,
                TradeModel.exit_time.isnot(None)
            ).all()

            if not completed:
                return {'period_days': days, 'total_trades': 0, 'win_rate': 0.0, 'total_pnl': 0.0}

            wins = sum(1 for t in completed if t.pnl > 0)
            total_pnl = sum(t.pnl for t in completed)

            return {
                'period_days': days,
                'total_trades': len(completed),
                'win_rate': (wins / len(completed)) * 100 if completed else 0,
                'total_pnl': total_pnl,
                'avg_pnl': total_pnl / len(completed) if completed else 0,
            }
