#!/usr/bin/env python3
"""
OMNIBOT v2.5.1 - Multi-Market Trading Engine
Supports: US Stocks, Asia Stocks, Forex
"""
import pandas as pd
import numpy as np
from datetime import datetime, time
from typing import Dict, List, Optional
import signal
import sys
import time
import pytz
import threading

sys.path.insert(0, '/home/biqu/omnibot/src')

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from config.settings import secure_settings, trading_config
import yfinance as yf
import talib


# MARKET CONFIGURATION
MARKETS = {
    'US': {
        'name': 'US Stocks',
        'timezone': 'America/New_York',
        'open': time(9, 30),
        'close': time(16, 0),
        'symbols': ['TQQQ', 'SOXL', 'TSLA', 'NVDA', 'AMD', 'AAPL', 'MSFT', 
                    'AMZN', 'GOOGL', 'META', 'SPY', 'QQQ', 'IWM'],
        'enabled': True
    },
    'JP': {
        'name': 'Tokyo Stock Exchange',
        'timezone': 'Asia/Tokyo',
        'open': time(9, 0),
        'close': time(15, 0),
        'symbols': ['7203.T', '6758.T', '9984.T', '6861.T', '7974.T'],
        'enabled': True
    },
    'HK': {
        'name': 'Hong Kong Exchange',
        'timezone': 'Asia/Hong_Kong',
        'open': time(9, 30),
        'close': time(16, 0),
        'symbols': ['0700.HK', '3690.HK', '9988.HK', '2318.HK', '1299.HK'],
        'enabled': True
    },
    'FOREX': {
        'name': 'Currency Trading',
        'timezone': 'UTC',  # Forex trades 24/5
        'open': time(0, 0),  # Sunday 5pm ET
        'close': time(23, 59),  # Friday 5pm ET
        'symbols': ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X', 
                    'USDCAD=X', 'USDCHF=X', 'NZDUSD=X', 'EURGBP=X'],
        'enabled': True,
        'is_24h': True  # Special flag for 24-hour market
    }
}


class Position:
    """Track open position"""
    def __init__(self, symbol, qty, entry_price, market='US'):
        self.symbol = symbol
        self.qty = qty
        self.entry_price = entry_price
        self.market = market
        self.entry_time = datetime.now()
        self.stop_loss = entry_price * 0.97  # -3%
        self.take_profit = entry_price * 1.06  # +6%


class MultiMarketEngine:
    """Multi-market trading engine - US, Asia, Forex"""

    def __init__(self):
        print("="*70)
        print("OMNIBOT v2.5.1 - MULTI-MARKET TRADING SYSTEM")
        print("US Stocks | Asia Stocks | Forex")
        print("="*70)

        # Connect to Alpaca
        self.trading_client = TradingClient(
            secure_settings.alpaca_api_key,
            secure_settings.alpaca_secret_key,
            paper=(secure_settings.trading_mode == 'paper')
        )

        # Track positions by market
        self.positions: Dict[str, Position] = {}

        # Strategy parameters
        self.rsi_entry = 40
        self.rsi_exit = 60
        self.running = True
        signal.signal(signal.SIGINT, self._signal_handler)

        print("✓ Engine initialized")
        print(f"✓ Mode: {secure_settings.trading_mode.upper()}")

        # Show market status
        for market_id, config in MARKETS.items():
            if config['enabled']:
                is_open = self.is_market_open(market_id)
                status = "🟢 OPEN" if is_open else "🔴 CLOSED"
                print(f"✓ {config['name']}: {status}")
        print()

    def _signal_handler(self, signum, frame):
        print("\nShutdown requested...")
        self.running = False
        sys.exit(0)

    def is_market_open(self, market_id: str) -> bool:
        """Check if a specific market is currently open"""
        config = MARKETS.get(market_id)
        if not config or not config['enabled']:
            return False

        # Get current time in market's timezone
        tz = pytz.timezone(config['timezone'])
        now = datetime.now(tz)
        current_time = now.time()

        # Forex is 24/5 (closed weekends)
        if config.get('is_24h'):
            return now.weekday() < 5  # Mon-Fri only

        # Regular market hours
        market_open = config['open']
        market_close = config['close']

        # Check if weekday (most markets closed Sat/Sun)
        if now.weekday() >= 5:
            return False

        return market_open <= current_time <= market_close

    def get_active_markets(self) -> List[str]:
        """Get list of currently open markets"""
        return [m for m in MARKETS if self.is_market_open(m)]

    def get_data(self, symbol: str, market: str = 'US'):
        """Get market data with timezone awareness"""
        try:
            ticker = yf.Ticker(symbol)

            # Different data periods for different markets
            if market == 'FOREX':
                df = ticker.history(period="1d", interval="5m")
            else:
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
        df['rsi'] = talib.RSI(df['close'], timeperiod=14)
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

    def enter_position(self, symbol, price, market='US'):
        """Enter a position"""
        try:
            account = self.trading_client.get_account()
            equity = float(account.equity)

            # Split equity across active markets
            active_markets = len(self.get_active_markets())
            if active_markets == 0:
                active_markets = 1

            # Position size: 15% per position, divided by active markets
            position_value = (equity * 0.15) / active_markets
            qty = int(position_value / price)

            if qty < 1:
                return False

            order = MarketOrderRequest(
                symbol=symbol, qty=qty, side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY
            )
            self.trading_client.submit_order(order)
            self.positions[symbol] = Position(symbol, qty, price, market)

            market_name = MARKETS[market]['name']
            print(f"🟢 [ENTRY] [{market}] {symbol}: Bought {qty} @ ${price:.2f}")
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

            print(f"🔴 [EXIT] [{pos.market}] {symbol}: Sold {pos.qty} @ ${price:.2f}")
            print(f"   Reason: {reason} | P&L: ${pnl:+.2f} ({pnl_pct:+.2f}%)")
            del self.positions[symbol]
            return True
        except Exception as e:
            return False

    def scan_market(self, market_id: str):
        """Scan all symbols in a specific market"""
        if not self.is_market_open(market_id):
            return

        config = MARKETS[market_id]

        for symbol in config['symbols']:
            if not self.running:
                break

            df = self.get_data(symbol, market_id)
            if df is None or len(df) < 20:
                continue

            df = self.calculate_indicators(df)
            price = df['close'].iloc[-1]
            rsi = df['rsi'].iloc[-1]

            # Check if we have a position
            if symbol in self.positions:
                should_exit, reason = self.check_exit(df, self.positions[symbol])
                print(f"[{market_id}] {symbol} ${price:.2f} RSI:{rsi:.1f} | {reason}")
                if should_exit:
                    self.exit_position(symbol, price, reason)
            else:
                # Check entry
                should_enter, info = self.check_entry(df)
                print(f"[{market_id}] {symbol} ${price:.2f} RSI:{info.get('rsi', 0):.1f} | Enter:{should_enter}")
                if should_enter:
                    self.enter_position(symbol, price, market_id)

    def trading_loop(self):
        """Main trading loop - scans all active markets"""
        print("\n" + "="*70)
        print("TRADING LOOP STARTED")
        print("Scanning all active markets every 10 seconds")
        print("="*70 + "\n")

        scan_count = 0

        while self.running:
            try:
                scan_count += 1
                active_markets = self.get_active_markets()

                print(f"\n--- Scan #{scan_count} | Active Markets: {', '.join(active_markets) or 'NONE'} ---")

                # Scan each active market
                for market_id in active_markets:
                    if not self.running:
                        break
                    self.scan_market(market_id)

                # If no markets open, wait and show status
                if not active_markets:
                    next_market = self.get_next_market_open()
                    if next_market:
                        print(f"⏳ All markets closed. Next: {next_market}")

                time.sleep(10)

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[ERROR] {e}")
                time.sleep(10)

        print("\nEngine stopped.")

    def get_next_market_open(self) -> Optional[str]:
        """Get info about next market to open"""
        now = datetime.now(pytz.UTC)

        for market_id, config in MARKETS.items():
            if not config['enabled']:
                continue
            # Simplified - just return first enabled market
            return f"{config['name']} at {config['open']} {config['timezone']}"
        return None

    def start(self):
        self.trading_loop()

    def stop(self):
        self.running = False


# Backward compatibility
TradingEngineV25 = MultiMarketEngine
TradingEngine = MultiMarketEngine
