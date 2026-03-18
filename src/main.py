#!/usr/bin/env python3
"""OMNIBOT v2.5.1 - Main Entry"""
import sys
sys.path.insert(0, '/home/biqu/omnibot/src')

def run_cli():
    from trading.engine import MultiMarketEngine
    print("\nOMNIBOT v2.5.1 - Multi-Market Trading\n")
    engine = MultiMarketEngine()
    try:
        engine.start()
    except KeyboardInterrupt:
        print("\nShutdown...")

if __name__ == "__main__":
    run_cli()
