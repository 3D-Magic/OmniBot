"""
OmniBot v2.6.1 Sentinel - Trading Engine
Handles aggressive trading modes and HFT scalping
"""

import random
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional

from config.settings import Settings, TradingMode

class TradingEngine:
    def __init__(self):
        self.positions = []
        self.trade_history = []
        self.is_running = False
        self.mode = TradingMode.AGGRESSIVE
        self.daily_pnl = 0
        self.daily_trades = 0
        self.last_trade_time = {}

        self.strategy_stats = {
            'momentum': {'trades': 0, 'wins': 0, 'profit': 0},
            'mean_reversion': {'trades': 0, 'wins': 0, 'profit': 0},
            'breakout': {'trades': 0, 'wins': 0, 'profit': 0},
            'ml_ensemble': {'trades': 0, 'wins': 0, 'profit': 0}
        }

    def start(self):
        self.is_running = True
        print(f"[ENGINE] Trading engine started in {self.mode.value.upper()} mode")

        if self.mode == TradingMode.HFT:
            threading.Thread(target=self._hft_loop, daemon=True).start()
        else:
            threading.Thread(target=self._trading_loop, daemon=True).start()

        threading.Thread(target=self._auto_close_monitor, daemon=True).start()

    def stop(self):
        self.is_running = False
        print("[ENGINE] Trading engine stopped")

    def set_mode(self, mode: TradingMode):
        self.mode = mode
        print(f"[ENGINE] Mode changed to: {mode.value.upper()}")

    def _trading_loop(self):
        while self.is_running:
            try:
                if self.mode != TradingMode.SENTINEL:
                    self._evaluate_strategies()

                sleep_times = {
                    TradingMode.CONSERVATIVE: 300,
                    TradingMode.MODERATE: 120,
                    TradingMode.AGGRESSIVE: 60,
                    TradingMode.HFT: 30
                }
                time.sleep(sleep_times.get(self.mode, 120))

            except Exception as e:
                print(f"[ENGINE] Error: {e}")
                time.sleep(60)

    def _hft_loop(self):
        print("[ENGINE] HFT mode active - scanning every 30 seconds")
        while self.is_running and self.mode == TradingMode.HFT:
            try:
                self._evaluate_strategies()
                time.sleep(30)
            except Exception as e:
                print(f"[ENGINE] HFT error: {e}")
                time.sleep(10)

    def _evaluate_strategies(self):
        strategies = ['momentum', 'mean_reversion', 'breakout', 'ml_ensemble']

        for strategy in strategies:
            last_trade = self.last_trade_time.get(strategy, 0)
            cooldown = 60 if self.mode == TradingMode.HFT else 300
            if time.time() - last_trade < cooldown:
                continue

            signal = self._generate_signal(strategy)

            if signal:
                self._execute_trade(strategy, signal)

    def _generate_signal(self, strategy: str) -> Optional[Dict]:
        base_confidence = {
            'momentum': 0.65,
            'mean_reversion': 0.60,
            'breakout': 0.62,
            'ml_ensemble': 0.70
        }

        confidence = base_confidence.get(strategy, 0.60) + (random.random() - 0.5) * 0.2

        thresholds = {
            TradingMode.CONSERVATIVE: 0.75,
            TradingMode.MODERATE: 0.65,
            TradingMode.AGGRESSIVE: 0.55,
            TradingMode.HFT: 0.48
        }

        threshold = thresholds.get(self.mode, 0.65)

        if confidence >= threshold:
            return {
                'direction': 'LONG' if random.random() > 0.4 else 'SHORT',
                'confidence': min(confidence, 0.95),
                'entry_price': random.uniform(100, 500),
                'stop_loss': random.uniform(0.02, 0.05),
                'take_profit': random.uniform(0.03, 0.08),
                'symbol': random.choice(['AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMZN'])
            }
        return None

    def _execute_trade(self, strategy: str, signal: Dict):
        if len(self.positions) >= Settings.MAX_CONCURRENT_POSITIONS:
            return

        if self.daily_pnl < -Settings.MAX_DAILY_LOSS * 100000:
            return

        portfolio_value = 100000
        risk_amount = portfolio_value * 0.05

        position_size = risk_amount / (signal['entry_price'] * signal['stop_loss'])

        trade = {
            'id': len(self.trade_history) + 1,
            'strategy': strategy,
            'symbol': signal['symbol'],
            'direction': signal['direction'],
            'entry_price': signal['entry_price'],
            'size': position_size,
            'stop_loss': signal['entry_price'] * (1 - signal['stop_loss']),
            'take_profit': signal['entry_price'] * (1 + signal['take_profit']),
            'entry_time': datetime.now(),
            'risk_amount': risk_amount,
            'confidence': signal['confidence']
        }

        self.positions.append(trade)
        self.trade_history.append(trade)
        self.last_trade_time[strategy] = time.time()
        self.daily_trades += 1

        print(f"[TRADE] {strategy.upper()} | {signal['symbol']} {signal['direction']} | Confidence: {signal['confidence']:.2%}")

        threading.Thread(target=self._monitor_position, args=(trade,), daemon=True).start()

    def _monitor_position(self, trade: Dict):
        max_hold = 300 if self.mode == TradingMode.HFT else 3600

        for _ in range(max_hold // 5):
            if trade not in self.positions:
                return

            current_price = trade['entry_price'] * (1 + (random.random() - 0.5) * 0.02)

            pnl_pct = (current_price - trade['entry_price']) / trade['entry_price']
            if trade['direction'] == 'SHORT':
                pnl_pct = -pnl_pct

            if current_price <= trade['stop_loss']:
                self._close_position(trade, current_price, 'STOP_LOSS')
                return
            elif current_price >= trade['take_profit']:
                self._close_position(trade, current_price, 'TAKE_PROFIT')
                return

            time.sleep(5)

        self._close_position(trade, current_price, 'TIME_EXIT')

    def _close_position(self, trade: Dict, exit_price: float, reason: str):
        if trade not in self.positions:
            return

        pnl = (exit_price - trade['entry_price']) * trade['size']
        if trade['direction'] == 'SHORT':
            pnl = -pnl

        trade['exit_price'] = exit_price
        trade['pnl'] = pnl
        trade['exit_reason'] = reason

        self.positions.remove(trade)
        self.daily_pnl += pnl

        stats = self.strategy_stats[trade['strategy']]
        stats['trades'] += 1
        stats['profit'] += pnl
        if pnl > 0:
            stats['wins'] += 1

        print(f"[CLOSE] {trade['strategy'].upper()} | P&L: ${pnl:.2f} | {reason}")

    def _auto_close_monitor(self):
        while self.is_running:
            try:
                now = datetime.now()

                if Settings.AUTO_CLOSE_ENABLED:
                    close_hour, close_minute = map(int, Settings.AUTO_CLOSE_TIME.split(':'))
                    if now.hour == close_hour and now.minute == close_minute:
                        self._close_all_positions("AUTO_CLOSE")

                if Settings.AUTO_CLOSE_WEEKEND and now.weekday() == 4:
                    if now.hour == 15 and now.minute == 30:
                        self._close_all_positions("WEEKEND_CLOSE")

                time.sleep(60)

            except Exception as e:
                time.sleep(60)

    def _close_all_positions(self, reason: str):
        for trade in self.positions[:]:
            exit_price = trade['entry_price'] * (1 + (random.random() - 0.5) * 0.01)
            self._close_position(trade, exit_price, reason)

    def get_stats(self) -> Dict:
        total_trades = sum(s['trades'] for s in self.strategy_stats.values())
        total_wins = sum(s['wins'] for s in self.strategy_stats.values())
        total_profit = sum(s['profit'] for s in self.strategy_stats.values())

        return {
            'mode': self.mode.value,
            'open_positions': len(self.positions),
            'daily_pnl': self.daily_pnl,
            'daily_trades': self.daily_trades,
            'total_trades': total_trades,
            'win_rate': (total_wins / total_trades * 100) if total_trades > 0 else 0,
            'total_profit': total_profit,
            'strategy_stats': self.strategy_stats
        }
