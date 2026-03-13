#!/usr/bin/env python3
"""OMNIBOT v2.5 - Main Entry Point"""
import sys
import os
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_configuration():
    """Verify configuration is present"""
    errors = []
    try:
        from config.settings import secure_settings
        if not secure_settings.alpaca_api_key:
            errors.append("ALPACA_API_KEY not configured")
        if not secure_settings.alpaca_secret_key:
            errors.append("ALPACA_SECRET_KEY not configured")
        if not secure_settings.database_url:
            errors.append("DATABASE_URL not configured")
    except Exception as e:
        errors.append(f"Settings error: {e}")

    if errors:
        print("\n❌ Configuration Errors:")
        for e in errors:
            print(f"  - {e}")
        print("\nRun: python src/main.py --setup")
        return False
    return True

def setup_encryption():
    """Interactive setup for API keys"""
    print("\n" + "=" * 70)
    print("OMNIBOT v2.5 - Security Setup")
    print("=" * 70 + "\n")

    print("Enter your API keys (saved to .env file):")
    print("-" * 50)

    alpaca_key = input("Alpaca API Key: ").strip()
    alpaca_secret = input("Alpaca Secret Key: ").strip()
    newsapi_key = input("NewsAPI Key (optional): ").strip() or ""
    db_choice = input("Use PostgreSQL? (y/n, default n): ").strip().lower()

    if db_choice == 'y':
        db_pass = input("PostgreSQL password: ").strip()
        db_url = f"postgresql://omnibot:{db_pass}@localhost:5432/omnibot_db"
    else:
        db_url = "sqlite:///omnibot.db"

    env_content = f"""# OMNIBOT v2.5 Configuration
# Generated: {datetime.now().isoformat()}

ALPACA_API_KEY_ENC='{alpaca_key}'
ALPACA_SECRET_KEY_ENC='{alpaca_secret}'
NEWSAPI_KEY_ENC='{newsapi_key}'
POLYGON_KEY_ENC=''

DATABASE_URL='{db_url}'
REDIS_URL='redis://localhost:6379/0'
TRADING_MODE='paper'

MODEL_PATH='./models'
DATA_PATH='./data'
"""

    with open('.env', 'w') as f:
        f.write(env_content)
    os.chmod('.env', 0o600)
    print(f"\n✓ Configuration saved to .env")

def show_trades(days=2, symbol=None, export=None):
    """Show recent trades"""
    print(f"\n{'=' * 80}")
    print(f"OMNIBOT v2.5 - Trade History (Last {days} Days)")
    print(f"{'=' * 80}\n")

    try:
        from database.manager import DatabaseManager
        from config.settings import secure_settings
        import pandas as pd

        db_manager = DatabaseManager(secure_settings.database_url)
        trades = db_manager.get_trades(days=days, symbol=symbol)

        if trades.empty:
            print("No trades found in the specified period.")
            return 0

        stats = db_manager.get_trade_statistics(days=days)
        print("SUMMARY STATISTICS:")
        print(f"  Period: Last {stats['period_days']} days")
        print(f"  Total Trades: {stats['total_trades']}")
        print(f"  Win Rate: {stats['win_rate']:.1f}%")
        print(f"  Total P&L: ${stats['total_pnl']:+.2f}")
        print()

        print(f"{'Time':<20} {'Symbol':<8} {'Side':<6} {'Qty':<8} {'Entry':<10} {'P&L':<12}")
        print("-" * 80)

        for _, trade in trades.iterrows():
            time_str = str(trade['entry_time'])[:16]
            pnl_str = f"${trade['pnl']:+.2f}" if pd.notna(trade['pnl']) else "--"
            print(f"{time_str:<20} {trade['symbol']:<8} {trade['side']:<6} "
                  f"{trade['qty']:<8} ${trade['entry_price']:<9.2f} {pnl_str:<12}")

        if export:
            trades.to_csv(export, index=False)
            print(f"\n✓ Exported to {export}")

        print(f"\n{'=' * 80}")
        return 0

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

def run_cli():
    """Run in CLI mode"""
    from trading.engine import TradingEngineV25

    print("\n" + "=" * 70)
    print("OMNIBOT v2.5 - CLI Mode")
    print("=" * 70 + "\n")

    if not check_configuration():
        return 1

    engine = TradingEngineV25()
    try:
        engine.start()
    except KeyboardInterrupt:
        print("\nShutdown by user")
    return 0

def main():
    parser = argparse.ArgumentParser(description='OMNIBOT v2.5 Trading System')
    parser.add_argument('--mode', choices=['cli', 'gui', 'backtest'], default='cli')
    parser.add_argument('--setup', action='store_true', help='Run initial setup')
    parser.add_argument('--trades', action='store_true', help='Show recent trades')
    parser.add_argument('--days', type=int, default=2)
    parser.add_argument('--symbol', type=str, default=None)
    parser.add_argument('--export', type=str, default=None)

    args = parser.parse_args()

    if args.setup:
        return setup_encryption()
    if args.trades:
        return show_trades(days=args.days, symbol=args.symbol, export=args.export)
    if args.mode == 'cli':
        return run_cli()
    else:
        print(f"Unknown mode: {args.mode}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
