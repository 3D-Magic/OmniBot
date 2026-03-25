"""
OMNIBOT Backtest Engine
Backtesting functionality for strategies
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

from config.settings import TRADING

logger = logging.getLogger(__name__)


@dataclass
class Trade:
    entry_date: datetime
    exit_date: Optional[datetime]
    symbol: str
    entry_price: float
    exit_price: Optional[float]
    quantity: float
    side: str
    pnl: Optional[float]
    pnl_percent: Optional[float]
    exit_reason: Optional[str]


class BacktestEngine:
    """Backtesting engine for trading strategies"""

    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions: Dict[str, Dict] = {}
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = []
        self.dates: List[datetime] = []

        logger.info(f"BacktestEngine initialized (capital: ${initial_capital})")

    def reset(self):
        """Reset backtest state"""
        self.capital = self.initial_capital
        self.positions = {}
        self.trades = []
        self.equity_curve = []
        self.dates = []

    def enter_position(self, symbol: str, price: float, 
                       date: datetime, side: str = "long") -> bool:
        """Enter a position"""
        if symbol in self.positions:
            return False

        # Calculate position size (10% of capital)
        position_value = self.capital * 0.1
        quantity = position_value / price

        self.positions[symbol] = {
            'entry_price': price,
            'quantity': quantity,
            'side': side,
            'entry_date': date,
            'highest_price': price,
            'stop_loss': price * 0.95  # 5% stop loss
        }

        return True

    def exit_position(self, symbol: str, price: float, 
                      date: datetime, reason: str = "signal") -> Optional[float]:
        """Exit a position"""
        if symbol not in self.positions:
            return None

        pos = self.positions[symbol]

        if pos['side'] == "long":
            pnl = (price - pos['entry_price']) * pos['quantity']
            pnl_percent = (price / pos['entry_price'] - 1) * 100
        else:
            pnl = (pos['entry_price'] - price) * pos['quantity']
            pnl_percent = (pos['entry_price'] / price - 1) * 100

        trade = Trade(
            entry_date=pos['entry_date'],
            exit_date=date,
            symbol=symbol,
            entry_price=pos['entry_price'],
            exit_price=price,
            quantity=pos['quantity'],
            side=pos['side'],
            pnl=pnl,
            pnl_percent=pnl_percent,
            exit_reason=reason
        )

        self.trades.append(trade)
        self.capital += pnl

        del self.positions[symbol]

        return pnl

    def update_positions(self, current_prices: Dict[str, float], date: datetime):
        """Update positions with current prices"""
        for symbol, price in current_prices.items():
            if symbol in self.positions:
                pos = self.positions[symbol]

                # Update trailing stop
                if price > pos['highest_price']:
                    pos['highest_price'] = price
                    pos['stop_loss'] = price * 0.95

                # Check stop loss
                if price <= pos['stop_loss']:
                    self.exit_position(symbol, price, date, "stop_loss")

    def run_backtest(self, data: Dict[str, pd.DataFrame], 
                     signals: Dict[str, List[str]]) -> Dict[str, Any]:
        """Run backtest with historical data"""
        self.reset()

        # Get all dates
        all_dates = set()
        for symbol, df in data.items():
            all_dates.update(df.index)

        sorted_dates = sorted(all_dates)

        for date in sorted_dates:
            # Update equity
            current_equity = self.capital
            for symbol, pos in self.positions.items():
                if symbol in data and date in data[symbol].index:
                    price = data[symbol].loc[date, 'Close']
                    if pos['side'] == "long":
                        current_equity += (price - pos['entry_price']) * pos['quantity']
                    else:
                        current_equity += (pos['entry_price'] - price) * pos['quantity']

            self.equity_curve.append(current_equity)
            self.dates.append(date)

            # Get current prices for position management
            current_prices = {}
            for symbol, df in data.items():
                if date in df.index:
                    current_prices[symbol] = df.loc[date, 'Close']

            # Update positions
            self.update_positions(current_prices, date)

            # Process signals
            for symbol, signal_list in signals.items():
                if symbol not in data:
                    continue

                date_idx = None
                if date in data[symbol].index:
                    date_idx = data[symbol].index.get_loc(date)

                if date_idx is not None and date_idx < len(signal_list):
                    signal = signal_list[date_idx]

                    if signal == "buy" and symbol not in self.positions:
                        price = data[symbol].loc[date, 'Close']
                        self.enter_position(symbol, price, date)

                    elif signal == "sell" and symbol in self.positions:
                        price = data[symbol].loc[date, 'Close']
                        self.exit_position(symbol, price, date, "signal")

        return self.get_results()

    def get_results(self) -> Dict[str, Any]:
        """Calculate backtest results"""
        if not self.trades:
            return {
                'total_return': 0,
                'total_trades': 0,
                'winning_trades': 0,
                'win_rate': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0
            }

        # Calculate metrics
        total_return = (self.capital - self.initial_capital) / self.initial_capital * 100
        total_trades = len(self.trades)
        winning_trades = sum(1 for t in self.trades if t.pnl and t.pnl > 0)
        win_rate = winning_trades / total_trades * 100

        # Max drawdown
        peak = self.initial_capital
        max_drawdown = 0
        for equity in self.equity_curve:
            if equity > peak:
                peak = equity
            drawdown = (peak - equity) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        # Sharpe ratio (simplified)
        if len(self.equity_curve) > 1:
            returns = pd.Series(self.equity_curve).pct_change().dropna()
            if returns.std() != 0:
                sharpe = (returns.mean() / returns.std()) * np.sqrt(252)
            else:
                sharpe = 0
        else:
            sharpe = 0

        return {
            'initial_capital': self.initial_capital,
            'final_capital': self.capital,
            'total_return': total_return,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': total_trades - winning_trades,
            'win_rate': win_rate,
            'max_drawdown': max_drawdown * 100,
            'sharpe_ratio': sharpe,
            'trades': [
                {
                    'symbol': t.symbol,
                    'entry': t.entry_date.strftime('%Y-%m-%d'),
                    'exit': t.exit_date.strftime('%Y-%m-%d') if t.exit_date else None,
                    'pnl': t.pnl,
                    'pnl_percent': t.pnl_percent,
                    'reason': t.exit_reason
                }
                for t in self.trades[-20:]  # Last 20 trades
            ]
        }


def create_backtest_engine(initial_capital: float = 10000.0) -> BacktestEngine:
    """Factory function"""
    return BacktestEngine(initial_capital)
