#!/usr/bin/env python3
"""
OMNIBOT v2.5 - Trading Engine
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import signal
import sys
import time
import uuid
import asyncio
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from config.settings import secure_settings, trading_config
from risk.manager import risk_manager
from ml.regime_detector import regime_detector, MarketRegime
from ml.lstm_predictor import market_predictor
from data.hybrid_client import data_client
from database.manager import db_manager, Trade
from utils.monitoring import monitor


class Position:
    """Position tracking"""
    def __init__(self, symbol, qty, avg_entry, stop_loss, take_profit, strategy_id):
        self.symbol = symbol
        self.qty = qty
        self.avg_entry = avg_entry
        self.current_price = avg_entry
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.entry_time = datetime.now()
        self.unrealized_pnl = 0.0


class TradingEngineV25:
    """OMNIBOT v2.5 Trading Engine"""

    def __init__(self, display_callback=None):
        print("=" * 70)
        print("OMNIBOT v2.5 - INTELLIGENT ADAPTIVE TRADING SYSTEM")
        print("ML-Enhanced Multi-Strategy Execution")
        print("=" * 70 + "\n")

        # CRITICAL FIX: Use trading_mode directly (string with use_enum_values=True)
        # DO NOT use .value here - it will cause AttributeError
        self.trading_client = TradingClient(
            secure_settings.alpaca_api_key,
            secure_settings.alpaca_secret_key,
            paper=(secure_settings.trading_mode == 'paper')
        )

        self.running = True
        self.open_positions: Dict[str, Position] = {}
        self.daily_stats = {'date': datetime.now().date(), 'trades': 0, 'pnl': 0.0, 'wins': 0, 'losses': 0}

        signal.signal(signal.SIGINT, self._signal_handler)
        self._sync_positions()

        print("✓ Engine initialized")
        print(f"✓ Mode: {secure_settings.trading_mode.upper()}")
        print(f"✓ Symbols: {len(trading_config.symbols)}")
        print(f"✓ ML Model: {'Active' if market_predictor else 'Standby'}")
        print()

    def _signal_handler(self, signum, frame):
        print("\nShutdown requested...")
        self.running = False
        sys.exit(0)

    def _sync_positions(self):
        try:
            broker_positions = self.trading_client.get_all_positions()
            for pos in broker_positions:
                symbol = pos.symbol
                if symbol not in self.open_positions:
                    self.open_positions[symbol] = Position(
                        symbol=symbol,
                        qty=int(float(pos.qty)),
                        avg_entry=float(pos.avg_entry_price),
                        stop_loss=float(pos.avg_entry_price) * 0.97,
                        take_profit=float(pos.avg_entry_price) * 1.06,
                        strategy_id='synced'
                    )
            print(f"✓ Synced {len(self.open_positions)} positions")
        except Exception as e:
            print(f"Sync error: {e}")

    def get_account(self):
        try:
            acc = self.trading_client.get_account()
            return {
                'equity': float(acc.equity),
                'cash': float(acc.cash),
                'buying_power': float(acc.buying_power),
                'daytrade_count': int(acc.daytrade_count) if hasattr(acc, 'daytrade_count') else 0
            }
        except Exception as e:
            return {'equity': 0, 'cash': 0, 'buying_power': 0, 'daytrade_count': 0}

    # CRITICAL FIX: Made _run_stream a regular method, not async
    def _run_stream(self):
        """Stream handler - runs in separate thread to avoid async issues"""
        try:
            # Websocket streaming disabled - using REST polling instead
            # This avoids asyncio coroutine issues on Raspberry Pi
            pass
        except Exception as e:
            print(f"Stream setup error: {e}")

    def _scan_symbols(self):
        """Scan all symbols for trading opportunities"""
        try:
            for symbol in trading_config.symbols:
                if not self.running:
                    break
                # Get latest data
                df = data_client.get_bars(symbol, limit=100)
                if df is None or df.empty:
                    continue

                # Check if we already have a position
                if symbol in self.open_positions:
                    self._manage_position(symbol, df)
                else:
                    self._check_entry(symbol, df)

        except Exception as e:
            print(f"Scan error: {e}")

    def _manage_position(self, symbol, df):
        """Manage existing position"""
        try:
            pos = self.open_positions[symbol]
            current_price = df['close'].iloc[-1] if 'close' in df.columns else pos.current_price

            # Update unrealized P&L
            pos.current_price = current_price
            pos.unrealized_pnl = (current_price - pos.avg_entry) * pos.qty

            # Check stop loss
            if current_price <= pos.stop_loss:
                self._exit_position(symbol, current_price, 'stop_loss')
                return

            # Check take profit
            if current_price >= pos.take_profit:
                self._exit_position(symbol, current_price, 'take_profit')
                return

        except Exception as e:
            print(f"Position management error for {symbol}: {e}")

    def _check_entry(self, symbol, df):
        """Check for entry signals"""
        try:
            # Simple entry logic - can be enhanced with ML
            if len(df) < 20:
                return

            # Get prediction
            prediction = market_predictor.predict(symbol, df)

            # Check risk
            account = self.get_account()
            if account['equity'] <= 0:
                return

            # Entry conditions
            if prediction.confidence > 0.6 and prediction.direction in ['long', 'buy']:
                self._enter_position(symbol, df, prediction)

        except Exception as e:
            print(f"Entry check error for {symbol}: {e}")

    def _enter_position(self, symbol, df, prediction):
        """Enter a new position"""
        try:
            account = self.get_account()
            current_price = df['close'].iloc[-1]

            # Calculate position size
            max_position_value = account['equity'] * trading_config.max_position_pct
            qty = int(max_position_value / current_price)

            if qty < 1:
                return

            # Place order
            order = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY
            )

            self.trading_client.submit_order(order)

            # Track position
            stop_loss = current_price * 0.97
            take_profit = current_price * 1.06

            self.open_positions[symbol] = Position(
                symbol=symbol,
                qty=qty,
                avg_entry=current_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                strategy_id='v2.5'
            )

            # Save to database
            trade = Trade(
                id=str(uuid.uuid4()),
                symbol=symbol,
                side='buy',
                qty=qty,
                entry_price=current_price,
                entry_time=datetime.now(),
                strategy_id='v2.5',
                signal_confidence=prediction.confidence,
                ml_prediction=prediction.predicted_return
            )
            db_manager.save_trade(trade)

            self.daily_stats['trades'] += 1
            print(f"[ENTRY] {symbol} | Qty: {qty} | Price: ${current_price:.2f}")

        except Exception as e:
            print(f"Entry error for {symbol}: {e}")

    def _exit_position(self, symbol, exit_price, reason):
        """Exit an existing position"""
        try:
            pos = self.open_positions[symbol]

            # Place sell order
            order = MarketOrderRequest(
                symbol=symbol,
                qty=pos.qty,
                side=OrderSide.SELL,
                time_in_force=TimeInForce.DAY
            )

            self.trading_client.submit_order(order)

            # Calculate P&L
            pnl = (exit_price - pos.avg_entry) * pos.qty
            pnl_pct = ((exit_price - pos.avg_entry) / pos.avg_entry) * 100

            # Update database
            trade_id = str(uuid.uuid4())
            db_manager.update_trade_exit(
                trade_id=trade_id,
                exit_price=exit_price,
                exit_time=datetime.now(),
                pnl=pnl,
                exit_reason=reason
            )

            # Update stats
            self.daily_stats['pnl'] += pnl
            if pnl > 0:
                self.daily_stats['wins'] += 1
            else:
                self.daily_stats['losses'] += 1

            print(f"[EXIT] {symbol} | Reason: {reason} | P&L: ${pnl:+.2f} ({pnl_pct:+.2f}%)")

            # Remove from tracking
            del self.open_positions[symbol]

        except Exception as e:
            print(f"Exit error for {symbol}: {e}")

    def trading_loop(self):
        """Main trading loop"""
        print("\n" + "=" * 70)
        print("TRADING LOOP STARTED")
        print("=" * 70 + "\n")

        loop_count = 0

        while self.running:
            try:
                loop_count += 1

                # Check if market is open
                try:
                    clock = self.trading_client.get_clock()
                    if not clock.is_open and trading_config.market_open_only:
                        time.sleep(60)
                        continue
                except:
                    pass

                # Scan for trades
                self._scan_symbols()

                # Periodic status update
                if loop_count % 12 == 0:
                    account = self.get_account()
                    unrealized = sum(p.unrealized_pnl for p in self.open_positions.values())
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                          f"Equity: ${account['equity']:,.2f} | "
                          f"Positions: {len(self.open_positions)} | "
                          f"Unrealized: ${unrealized:+.2f}")

                time.sleep(trading_config.scan_interval)

            except Exception as e:
                print(f"Loop error: {e}")
                time.sleep(5)

    def start(self):
        """Start the trading engine"""
        # Start stream in background (optional, disabled for stability)
        self._run_stream()

        # Run main loop
        self.trading_loop()

    def stop(self):
        """Stop the trading engine"""
        self.running = False
        print("Trading engine stopped")


# Backwards compatibility
TradingEngine = TradingEngineV25
