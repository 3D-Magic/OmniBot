#!/usr/bin/env python3
"""
OmniBot v2.5 - Quick Test Script
"""
import sys
import os

sys.path.insert(0, '/home/Omnibot/omnibot/src')

def test_imports():
    """Test all module imports"""
    print("Testing imports...")
    try:
        from config.settings import secure_settings, trading_config
        print("✓ Config module")

        from database.manager import DatabaseManager, db_manager, Trade
        print("✓ Database module")

        from ml.lstm_predictor import MarketPredictor, market_predictor
        print("✓ ML module")

        from ml.regime_detector import RegimeDetector, regime_detector
        print("✓ Regime detector")

        from risk.manager import RiskManager, risk_manager
        print("✓ Risk module")

        from data.hybrid_client import HybridDataClient, data_client
        print("✓ Data module")

        from utils.monitoring import Monitoring, monitor
        print("✓ Utils module")

        from trading.engine import TradingEngineV25, TradingEngine, Position
        print("✓ Trading engine")

        print("\n✅ All imports successful!")
        return True
    except Exception as e:
        print(f"\n❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    try:
        from config.settings import secure_settings, trading_config

        print(f"Trading mode: {secure_settings.trading_mode}")
        print(f"Symbols: {len(trading_config.symbols)}")
        print(f"Max position: {trading_config.max_position_pct*100}%")
        print(f"Scan interval: {trading_config.scan_interval}s")

        print("\n✅ Configuration loaded!")
        return True
    except Exception as e:
        print(f"\n❌ Config error: {e}")
        return False

def test_database():
    """Test database connection"""
    print("\nTesting database...")
    try:
        from database.manager import db_manager

        # Try to get stats (will work even if empty)
        stats = db_manager.get_trade_statistics(days=7)
        print(f"Total trades (last 7 days): {stats['total_trades']}")

        print("\n✅ Database connected!")
        return True
    except Exception as e:
        print(f"\n❌ Database error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("OmniBot v2.5 - System Test")
    print("=" * 60)

    results = []
    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Database", test_database()))

    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)

    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:20} {status}")

    all_passed = all(r[1] for r in results)

    if all_passed:
        print("\n🎉 All tests passed! Ready to trade.")
        sys.exit(0)
    else:
        print("\n⚠️ Some tests failed. Check errors above.")
        sys.exit(1)
