# OmniBot v2.5 - Intelligent Adaptive Trading System

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Alpaca](https://img.shields.io/badge/Alpaca-Paper%20Trading-green.svg)](https://alpaca.markets/)

An ML-enhanced, multi-strategy algorithmic trading bot designed for Raspberry Pi 4 or higher with a minimum 8 GB RAM, featuring deep learning market prediction, risk management, and automated paper trading.

## 🚀 Features

- **ML-Powered Predictions**: LSTM neural networks for market direction forecasting
- **Risk Management**: Position sizing, stop-loss (3%), and take-profit (6%) automation
- **Multi-Asset Support**: Trade 13 popular symbols (TQQQ, SOXL, TSLA, NVDA, etc.)
- **Paper Trading**: Test strategies risk-free with Alpaca paper trading
- **24/7 Operation**: Systemd service for automatic startup and monitoring
- **Database Logging**: PostgreSQL/SQLite for trade history and analytics
- **Market Regime Detection**: Adaptive strategies based on market conditions

## 📋 Requirements

### Hardware
- Raspberry Pi 4 (8GB or more RAM recommended)
- MicroSD card (32GB or larger, Class 10)
- Ethernet cable or WiFi connection
- Power supply for Raspberry Pi

### Software
- Raspberry Pi OS (64-bit)
- Python 3.9+
- PostgreSQL 13+
- Redis 6+

## 🛠️ Installation

### 1. Clone Repository
```bash
git clone https://github.com/3D-Magic/OmniBot.git
cd OmniBot
```

### 2. Run Automated Setup
```bash
bash setup.sh
```

### 3. Add Your API Keys
```bash
nano ~/omnibot/.env
```

Fill in your Alpaca API keys from [https://alpaca.markets](https://alpaca.markets)

### 4. Test
```bash
python test_system.py
```

### 5. Start Trading
```bash
sudo systemctl start omnibot-v2.5.service
```

**That's it!** The bot will automatically start trading when the US market opens.

## 🎯 Usage

### Check Status
```bash
sudo systemctl status omnibot-v2.5.service
```

### View Live Logs
```bash
sudo journalctl -u omnibot-v2.5.service -f
```

### View Recent Trades
```bash
cd ~/omnibot
source venv/bin/activate
python src/main.py --trades
```

### View Last 7 Days
```bash
python src/main.py --trades --days 7
```

### Export Trades
```bash
python src/main.py --trades --export trades.csv
```

### Manual Setup (if needed)
```bash
python src/main.py --setup
```

## ⚙️ Configuration

### Trading Symbols
Edit `src/config/settings.py`:
```python
symbols: List[str] = [
    'TQQQ', 'SOXL', 'TSLA', 'NVDA', 'AMD', 'AAPL',
    'MSFT', 'AMZN', 'GOOGL', 'META', 'SPY', 'QQQ', 'IWM'
]
```

### Risk Parameters
```python
max_position_pct: float = 0.15  # 15% max per position
scan_interval: int = 10         # Scan every 10 seconds
market_open_only: bool = True   # Only trade during market hours
```

### Switch to Live Trading
⚠️ **WARNING**: Only switch after thorough paper testing!

Edit `.env`:
```bash
TRADING_MODE='live'
```

## 📊 Project Structure

```
omnibot/
├── src/
│   ├── config/          # Configuration management
│   ├── data/            # Data clients (Alpaca, Yahoo)
│   ├── database/        # PostgreSQL/SQLite models
│   ├── ml/              # LSTM predictor & regime detection
│   ├── risk/            # Risk management
│   ├── trading/         # Main trading engine
│   ├── utils/           # Monitoring & utilities
│   ├── gui/             # GUI placeholder
│   ├── tests/           # Unit tests
│   └── main.py          # Entry point
├── logs/                # Log files
├── data/                # Market data cache
├── models/              # ML model storage
├── backups/             # Database backups
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
├── omnibot-v2.5.service # Systemd service file
└── README.md            # This file
```

## 🔧 Troubleshooting

### Error: "asyncio not defined"
**Fix**: Already fixed in v2.5 - `import asyncio` added to engine.py

### Error: "coroutine never awaited"
**Fix**: Websocket streaming disabled, using REST polling instead

### Error: "ModuleNotFoundError: No module named 'hmmlearn'"
```bash
source ~/omnibot/venv/bin/activate
pip install hmmlearn
sudo systemctl restart omnibot-v2.5.service
```

### Database Connection Errors
```bash
sudo systemctl status postgresql
sudo systemctl start postgresql
sudo -u postgres psql -c "\l" | grep omnibot_db
```

### Check Service Logs
```bash
sudo journalctl -u omnibot-v2.5.service -n 50
```

## 🛡️ Security Notes

- **Never commit `.env` file** - it contains your API keys
- **Use paper trading first** - always test thoroughly before live trading
- **Secure your Raspberry Pi** - use strong passwords and keep it updated
- **API keys provide account access** - treat them like passwords
- **Regular backups** - backup your database and configuration

## 📈 Performance Expectations

- **Scan Interval**: 10 seconds (configurable)
- **Latency**: ~100-500ms for order execution (paper trading)
- **Positions**: Max 15% equity per position
- **Risk**: 3% stop loss, 6% take profit per trade
- **Trading Hours**: US Market (9:30 AM - 4:00 PM ET)

## 📝 License

Distributed under the Personal Use License. See `LICENSE` for more information.

## 🙏 Acknowledgments

- [Alpaca Markets](https://alpaca.markets/) for commission-free trading API
- [PyTorch](https://pytorch.org/) for deep learning framework
- [SQLAlchemy](https://www.sqlalchemy.org/) for database ORM

## ⚠️ Disclaimer

**This software is for educational purposes only. Trading stocks involves substantial risk of loss. Past performance is not indicative of future results. Always use paper trading to test strategies before risking real capital.**

---

**Happy Trading! 🚀**
