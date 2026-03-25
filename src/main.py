#!/usr/bin/env python3
"""
OmniBot v2.6.1 Sentinel - Main Entry Point
"""

import sys
import os
import argparse

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import Settings, TradingMode
from src.core.trading_engine import TradingEngine
from src.core.auto_updater import AutoUpdater
from src.dashboard.server import run_dashboard
import threading

def main():
    parser = argparse.ArgumentParser(description="OmniBot v2.6.1 Sentinel")
    parser.add_argument("--mode", type=str, default="aggressive",
                       choices=["conservative", "moderate", "aggressive", "hft", "sentinel"],
                       help="Trading mode")
    args = parser.parse_args()

    # Set trading mode
    Settings.set_trading_mode(args.mode)
    mode = Settings.TRADING_MODE

    print("\n" + "="*60)
    print("    🤖  OMNIBOT v2.6.1 Sentinel")
    print("="*60)
    print(f"    Mode: {mode.value.upper()}")
    print(f"    Auto-Update: {'Enabled' if Settings.AUTO_UPDATE_ENABLED else 'Disabled'}")
    print("="*60 + "\n")

    # Initialize components
    engine = TradingEngine()
    engine.set_mode(mode)

    updater = AutoUpdater(Settings)

    # Start trading engine (unless in sentinel mode)
    if mode != TradingMode.SENTINEL:
        engine.start()
        print(f"[MAIN] Trading engine started in {mode.value.upper()} mode")
    else:
        print("[MAIN] Sentinel mode - monitoring only")

    # Start auto-updater
    updater.start()

    # Start dashboard in main thread
    print("[MAIN] Starting dashboard...")
    run_dashboard(port=Settings.DASHBOARD_PORT)

if __name__ == "__main__":
    main()
