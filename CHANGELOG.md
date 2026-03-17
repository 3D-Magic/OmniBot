# Changelog

## v2.5.1 - 2026-03-18

### Fixed
- **Data Client**: Switched from Alpaca paid data to Yahoo Finance (free) to avoid "subscription does not permit querying recent SIP data" error
- **ML Predictor**: Fixed `KeyError: 'timestamp'` by using `df.index` instead of `df['timestamp']` in `_prepare_features()`
- **Monitoring**: Disabled HTTP server to prevent `ConnectionResetError: [Errno 104] Connection reset by peer`
- **Module Imports**: Cleaned up `ml/__init__.py` and `data/__init__.py` to remove non-existent imports (`online_learner`, `DataQualityMetrics`)
- **Asyncio**: Added `import asyncio` to engine.py to prevent "asyncio not defined" errors
- **Websocket**: Disabled async websocket streaming to prevent "coroutine never awaited" warnings

### Changed
- Data source now uses Yahoo Finance 5-minute bars (free) instead of Alpaca real-time data (paid)
- ML prediction now uses simple rule-based strategy (price vs SMA20) while LSTM model loads
- Bot now runs stable on Raspberry Pi without connection errors

### Known Issues
- Yahoo Finance data has 15-20 minute delay (acceptable for this strategy)
- ML model is currently rule-based; full LSTM implementation coming in v2.6
