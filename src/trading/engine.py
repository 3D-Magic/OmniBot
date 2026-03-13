#!/usr/bin/env python3
"""
OMNIBOT v2.5 - Trading Engine
Copyright (c) 2026 3D-Magic

LICENSE: Personal Use Only
- Free for individual personal trading
- NO sale, NO modifications, NO redistribution
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
import signal
import sys
import time
import uuid
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

from config.settings import secure_settings, trading_config
from risk.manager import risk_manager
from ml.regime_detector import regime_detector, MarketRegime
from ml.lstm_predictor import market_predictor
from data.hybrid_client import data_client
from database.manager import DatabaseManager, Trade
from utils.monitoring import monitor
from security.protector import protector

class Position:
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
    def __init__(self, display_callback=None):
        print("=" * 70)
        print("OMNIBOT v2.5 - INTELLIGENT ADAPTIVE TRADING SYSTEM")
        print(protector.get_license_watermark())
        print("=" * 70 + "\n")

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
        print(f"✓ ML Model: Active")
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
            print(f"⚠ Sync error: {e}")

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
            print(f"⚠ Account error: {e}")
            return {'equity': 0, 'cash': 0, 'buying_power': 0, 'daytrade_count': 0}

    def trading_loop(self):
        print("\n" + "=" * 70)
        print("TRADING LOOP STARTED")
        print(protector.get_license_watermark())
        print("=" * 70 + "\n")

        loop_count = 0
        while self.running:
            try:
                loop_count += 1

                try:
                    clock = self.trading_client.get_clock()
                    if not clock.is_open and trading_config.market_open_only:
                        time.sleep(60)
                        continue
                except:
                    pass

                if loop_count % 12 == 0:
                    account = self.get_account()
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                          f"Equity: ${account['equity']:,.2f} | "
                          f"Positions: {len(self.open_positions)} | "
                          f"PnL Today: ${self.daily_stats['pnl']:+.2f}")

                time.sleep(trading_config.scan_interval)

            except Exception as e:
                print(f"⚠ Loop error: {e}")
                time.sleep(10)

    def start(self):
        self.trading_loop()

    def stop(self):
        self.running = False
        print("Trading engine stopped")

TradingEngine = TradingEngineV25
