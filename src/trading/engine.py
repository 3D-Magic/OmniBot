#!/usr/bin/env python3
"""
OMNIBOT v2.5.1 - WORKING Trading Engine
Actually places trades using RSI + SMA strategy
Includes automated weekend updates
"""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict
import signal
import sys
import time
import threading

sys.path.insert(0, '/home/biqu/omnibot/src')

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from config.settings import secure_settings, trading_config
import yfinance as yf
import talib


class Position:
    """Track open position"""
    def __init__(self, symbol, qty, entry_price):
        self.symbol = symbol
        self.qty = qty
        self.entry_price = entry_price
        self.entry_time = datetime.now()
        self.stop_loss = entry_price * 0.97  # -3%
        self.take_profit = entry_price * 1.06  # +6%


class TradingEngineV25:
    """WORKING Trading Engine v2.5.1 - Actually trades!"""

    def __init__(self):
        print("="*70)
        print("OMNIBOT v2.5.1 - INTELLIGENT ADAPTIVE TRADING SYSTEM")
        print("ML-Enhanced Multi-Strategy Execution")
        print("="*70)

        # Connect to Alpaca Trading
        self.trading_client = TradingClient(
            secure_settings.alpaca_api_key,
            secure_settings.alpaca_secret_key,
            paper=(secure_settings.trading_mode == 'paper')
        )

        # Track positions
        self.positions: Dict[str, Position] = {}

        # Strategy parameters
        self.rsi_period = 14
        self.rsi_entry = 40      # Enter when RSI < 40
        self.rsi_exit = 60       # Exit when RSI > 60
        self.stoploss_pct = 0.03
        self.takeprofit_pct = 0.06

        # Running flag
        self.running = True
        signal.signal(signal.SIGINT, self._signal_handler)

        # Auto-update settings
        self.update_check_interval = 3600  # Check every hour
        self.last_update_check = 0

        print("✓ Engine initialized")
        print(f"✓ Mode: {secure_settings.trading_mode.upper()}")
        print(f"✓ Symbols: {len(trading_config.symbols)}")
        print("✓ Auto-update: Enabled (weekends only)")
        print()

    def _signal_handler(self, signum, frame):
        print("\nShutdown requested...")
        self.running = False
        sys.exit(0)

    def check_for_updates(self):
        """Check and perform auto-updates (weekends only)"""
        try:
            from auto_update import AutoUpdater
            updater = AutoUpdater()

            # Only check if enough time passed
            if not updater.should_check_update():
                return

            # Run update check in background thread
            update_thread = threading.Thread(target=updater.run, daemon=True)
            update_thread.start()

        except Exception as e:
            print(f"[AUTO-UPDATE] Error: {e}")

    def get_data(self, symbol: str):
        """Get data from Yahoo Finance (free)"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="3d", interval="5m")
            if df.empty:
                return None
            df = df.rename(columns={
                'Open': 'open', 'High': 'high', 'Low': 'low',
                'Close': 'close', 'Volume': 'volume'
            })
            return df
        except Exception as e:
            return None

    def calculate_indicators(self, df):
        """Calculate RSI and SMA"""
        df['rsi'] = talib.RSI(df['close'], timeperiod=self.rsi_period)
        df['sma20'] = talib.SMA(df['close'], timeperiod=20)
        return df

    def check_entry(self, df):
        """Check entry signal"""
        if len(df) < 20 or pd.isna(df['rsi'].iloc[-1]):
            return False, {}
        current = df.iloc[-1]
        price, rsi, sma20 = current['close'], current['rsi'], current['sma20']
        should_enter = (rsi < self.rsi_entry) and (price > sma20 * 0.98)
        return should_enter, {"price": price, "rsi": rsi}

    def check_exit(self, df, position):
        """Check exit signal"""
        current = df.iloc[-1]
        price, rsi = current['close'], current['rsi']
        if price <= position.stop_loss:
            return True, "Stop Loss"
        if price >= position.take_profit:
            return True, "Take Profit"
        if rsi > self.rsi_exit:
            return True, f"RSI Exit ({rsi:.1f})"
        return False, "Hold"

    def enter_position(self, symbol, price):
        """Enter a long position"""
        try:
            account = self.trading_client.get_account()
            equity = float(account.equity)
            qty = int((equity * 0.15) / price)
            if qty < 1:
                return False

            order = MarketOrderRequest(
                symbol=symbol, qty=qty, side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY
            )
            self.trading_client.submit_order(order)
            self.positions[symbol] = Position(symbol, qty, price)
            print(f"🟢 [ENTRY] {symbol}: Bought {qty} shares @ ${price:.2f}")
            return True
        except Exception as e:
            print(f"[ERROR] {symbol}: {e}")
            return False

    def exit_position(self, symbol, price, reason):
        """Exit a position"""
        try:
            pos = self.positions[symbol]
            order = MarketOrderRequest(
                symbol=symbol, qty=pos.qty, side=OrderSide.SELL,
                time_in_force=TimeInForce.DAY
            )
            self.trading_client.submit_order(order)
            pnl = (price - pos.entry_price) * pos.qty
            pnl_pct = ((price - pos.entry_price) / pos.entry_price) * 100
            print(f"🔴 [EXIT] {symbol}: Sold {pos.qty} shares @ ${price:.2f}")
            print(f"   Reason: {reason} | P&L: ${pnl:+.2f} ({pnl_pct:+.2f}%)")
            del self.positions[symbol]
            return True
        except Exception as e:
            return False

    def scan_symbol(self, symbol):
        """Scan a single symbol"""
        df = self.get_data(symbol)
        if df is None or len(df) < 20:
            return
        df = self.calculate_indicators(df)
        price = df['close'].iloc[-1]
        rsi = df['rsi'].iloc[-1]

        if symbol in self.positions:
            should_exit, reason = self.check_exit(df, self.positions[symbol])
            print(f"[{symbol}] ${price:.2f} | RSI: {rsi:.1f} | {reason}")
            if should_exit:
                self.exit_position(symbol, price, reason)
        else:
            should_enter, info = self.check_entry(df)
            print(f"[{symbol}] ${price:.2f} | RSI: {info.get('rsi', 0):.1f} | Enter: {should_enter}")
            if should_enter:
                self.enter_position(symbol, price)

    def trading_loop(self):
        """Main trading loop with auto-update checks"""
        print("\n" + "="*70)
        print("TRADING LOOP STARTED")
        print("Auto-update: Enabled (checks every hour)")
        print("="*70 + "\n")

        scan_count = 0
        last_update_check = 0

        while self.running:
            try:
                scan_count += 1
                now = time.time()

                # Check for updates every hour
                if now - last_update_check > self.update_check_interval:
                    self.check_for_updates()
                    last_update_check = now

                print(f"\n--- Scan #{scan_count} ---")
                for symbol in trading_config.symbols:
                    if not self.running:
                        break
                    self.scan_symbol(symbol)
                time.sleep(10)

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[ERROR] {e}")
                time.sleep(10)

        print("\nEngine stopped.")

    def start(self):
        self.trading_loop()

    def stop(self):
        self.running = False


TradingEngine = TradingEngineV25
