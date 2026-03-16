# OmniBot v2.5 - Intelligent Adaptive Trading System

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Alpaca](https://img.shields.io/badge/Alpaca-Paper%20Trading-green.svg)](https://alpaca.markets/)

An ML-enhanced, multi-strategy algorithmic trading bot designed for Raspberry Pi 4, featuring deep learning market prediction, risk management, and automated paper trading.

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
- Raspberry Pi 4 (4GB or 8GB RAM recommended)
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
git clone https://github.com/yourusername/omnibot-v2.5.git
cd omnibot-v2.5
```

### 2. Install System Dependencies
```bash
sudo apt update && sudo apt full-upgrade -y
sudo apt install -y python3-venv python3-pip python3-dev build-essential     libopenblas-dev liblapack-dev gfortran postgresql libpq-dev     redis-server git vim htop tree tmux sqlite3 libsqlite3-dev     pkg-config cmake libhdf5-dev
```

### 3. Setup Database
```bash
# Generate password
openssl rand -base64 32

# Create database
sudo systemctl enable postgresql
sudo systemctl start postgresql
sudo -u postgres psql <<EOF
CREATE USER Omnibot WITH PASSWORD 'YOUR_DB_PASSWORD_HERE';
CREATE DATABASE omnibot_db OWNER Omnibot;
GRANT ALL PRIVILEGES ON DATABASE omnibot_db TO Omnibot;
\q
EOF
```

### 4. Setup Redis
```bash
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### 5. Create Directory Structure
```bash
mkdir -p ~/omnibot/{src/{config,data,database,ml,risk,trading,utils,gui,tests},logs,data,secrets,models,backups}
cd ~/omnibot
```

### 6. Install Python Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
python -m nltk.downloader punkt vader_lexicon stopwords wordnet
```

### 7. Configure API Keys
```bash
# Copy example config
cp .env.example .env

# Edit with your keys
nano .env
```

Fill in your Alpaca API keys from [https://alpaca.markets](https://alpaca.markets)

### 8. Copy Source Files
```bash
cp -r src/* ~/omnibot/src/
```

### 9. Install Systemd Service
```bash
sudo cp omnibot-v2.5.service /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/omnibot-v2.5.service
sudo systemctl daemon-reload
sudo systemctl enable omnibot-v2.5.service
sudo systemctl start omnibot-v2.5.service
```

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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

## 🙏 Acknowledgments

- [Alpaca Markets](https://alpaca.markets/) for commission-free trading API
- [PyTorch](https://pytorch.org/) for deep learning framework
- [SQLAlchemy](https://www.sqlalchemy.org/) for database ORM

## ⚠️ Disclaimer

**This software is for educational purposes only. Trading stocks involves substantial risk of loss. Past performance is not indicative of future results. Always use paper trading to test strategies before risking real capital.**

---

**Happy Trading! 🚀**
