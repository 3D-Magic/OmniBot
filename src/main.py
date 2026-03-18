#!/usr/bin/env python3
"""
OMNIBOT v3.0 - Main Entry Point
"""
import sys
import argparse
from datetime import datetime

sys.path.insert(0, '/home/biqu/omnibot/src')


def check_configuration():
    """Verify configuration"""
    errors = []
    try:
        from config.settings import secure_settings
        if not secure_settings.alpaca_api_key:
            errors.append("ALPACA_API_KEY not configured")
        if not secure_settings.alpaca_secret_key:
            errors.append("ALPACA_SECRET_KEY not configured")
    except Exception as e:
        errors.append(f"Settings error: {e}")

    if errors:
        print("\n❌ Configuration Errors:")
        for e in errors:
            print(f" - {e}")
        return False
    return True


def show_trades(days=2, symbol=None, export=None):
    """Show recent trades"""
    print(f"\n{'='*80}")
    print(f"OMNIBOT v3.0 - Trade History (Last {days} Days)")
    print(f"{'='*80}\n")

    try:
        from database.manager import db_manager
        import pandas as pd

        trades = db_manager.get_trades(days=days, symbol=symbol)

        if trades.empty:
            print("No trades found in the specified period.")
            return 0

        stats = db_manager.get_trade_statistics(days=days)
        print("SUMMARY STATISTICS:")
        print(f" Period: Last {stats['period_days']} days")
        print(f" Total Trades: {stats['total_trades']}")
        print(f" Win Rate: {stats['win_rate']:.1f}%")
        print(f" Total P&L: ${stats['total_pnl']:+.2f}")
        print()

        print(f"{'Time':<20} {'Symbol':<8} {'Side':<6} {'Qty':<8} {'Entry':<10} {'Exit':<10} {'P&L':<12}")
        print("-" * 80)

        for _, trade in trades.iterrows():
            time_str = str(trade['entry_time'])[:16]
            exit_str = f"${trade['exit_price']:.2f}" if pd.notna(trade['exit_price']) else "--"
            pnl_str = f"${trade['pnl']:+.2f}" if pd.notna(trade['pnl']) else "--"
            print(f"{time_str:<20} {trade['symbol']:<8} {trade['side']:<6} "
                  f"{trade['qty']:<8} ${trade['entry_price']:<9.2f} "
                  f"{exit_str:<10} {pnl_str:<12}")

        if export:
            trades.to_csv(export, index=False)
            print(f"\n✓ Exported to {export}")

        print(f"\n{'='*80}")
        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


def run_cli():
    """Run trading engine"""
    from trading.engine import TradingEngineV25

    print("\n" + "="*70)
    print("OMNIBOT v3.0 - WORKING Trading Engine")
    print("="*70 + "\n")

    if not check_configuration():
        return 1

    engine = TradingEngineV25()
    try:
        engine.start()
    except KeyboardInterrupt:
        print("\nShutdown requested...")
    return 0


def main():
    parser = argparse.ArgumentParser(description='OMNIBOT v3.0')
    parser.add_argument('--trades', action='store_true', help='Show trades')
    parser.add_argument('--days', type=int, default=2, help='Days of history')
    parser.add_argument('--symbol', type=str, default=None, help='Filter symbol')
    parser.add_argument('--export', type=str, default=None, help='Export file')

    args = parser.parse_args()

    if args.trades:
        return show_trades(days=args.days, symbol=args.symbol, export=args.export)

    return run_cli()


if __name__ == "__main__":
    sys.exit(main())
