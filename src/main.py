#!/usr/bin/env python3
"""
OMNIBOT v2.5 - Main Entry Point
Copyright (c) 2026 3D-Magic

LICENSE: Personal Use Only
- Free for individual personal trading
- NO sale, NO modifications, NO redistribution
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# SECURITY: Verify integrity BEFORE anything else
print("\n" + "="*70)
print("🔒 OMNIBOT v2.5 - LICENSE PROTECTION")
print("="*70)

try:
    from security.protector import verify_before_start
    if not verify_before_start():
        print("\n❌ Cannot start - License violation detected")
        sys.exit(1)
except Exception as e:
    print(f"\n❌ Security check failed: {e}")
    print("This software may have been tampered with.")
    sys.exit(1)

# Display license
print("\n📜 LICENSE: Personal Use Only")
print("   - Free for your personal trading")
print("   - NO modifications permitted")
print("   - NO redistribution allowed")
print("="*70 + "\n")

import argparse
from datetime import datetime

def check_configuration():
    """Verify all required configuration is present"""
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
    """Interactive setup for API keys - REQUIRES ADMIN PASSWORD"""
    from security.protector import protector

    # Verify admin before allowing setup
    if not protector.verify_admin():
        print("\n❌ Setup aborted - Admin authentication failed")
        return 1

    print("\n" + "=" * 70)
    print("OMNIBOT v2.5 - Security Setup")
    print("=" * 70 + "\n")

    print("⚠️  WARNING: You are modifying protected configuration.")
    print("This is logged and monitored.\n")

    print("Enter your API keys (they will be saved to .env file):")
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
# LICENSE: Personal Use Only

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

    # Regenerate hashes after setup
    protector._generate_hashes()

    print(f"\n✓ Configuration saved to .env")
    print("✓ Integrity hashes updated")
    return 0

def show_trades(days=2, symbol=None, export=None):
    """Show recent trades with license watermark"""
    from security.protector import protector

    print(f"\n{'=' * 80}")
    print(f"OMNIBOT v2.5 - Trade History")
    print(protector.get_license_watermark())
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
    """Run in CLI mode with protection"""
    from trading.engine import TradingEngineV25
    from security.protector import protector

    print("\n" + "=" * 70)
    print("OMNIBOT v2.5 - Protected Trading System")
    print(protector.get_license_watermark())
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
    """Main entry point"""
    parser = argparse.ArgumentParser(description='OMNIBOT v2.5 Trading System')
    parser.add_argument('--mode', choices=['cli', 'gui', 'backtest'], default='cli')
    parser.add_argument('--setup', action='store_true', help='Run initial setup (requires admin)')
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
