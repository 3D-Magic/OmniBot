# OmniBot v3.0 - Working Trading System

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Alpaca](https://img.shields.io/badge/Alpaca-Paper%20Trading-green.svg)](https://alpaca.markets/)

An ML-enhanced, multi-strategy algorithmic trading bot designed for Raspberry Pi 4, featuring RSI-based market signals, automated risk management, and paper trading.

## 🚀 Features

- **RSI-Based Trading**: Mean reversion strategy with RSI < 40 entry, RSI > 60 exit
- **Risk Management**: Automatic 3% stop-loss and 6% take-profit
- **Multi-Asset Support**: Trade 13 popular symbols (TQQQ, SOXL, TSLA, NVDA, etc.)
- **Paper Trading**: Test strategies risk-free with Alpaca paper trading
- **24/7 Operation**: Systemd service for automatic startup and monitoring
- **Weekend Updates**: Safe update mechanism that preserves API keys

## 📋 Requirements

### Hardware
- Raspberry Pi 4 (4GB or 8GB RAM recommended)
- MicroSD card (32GB or larger, Class 10)
- Power supply for Raspberry Pi
- Ethernet cable or WiFi connection

### Software
- Raspberry Pi OS (64-bit)
- Python 3.9+
- PostgreSQL 13+
- Redis 6+

## 🛠️ Installation

### Option 1: Quick Start (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/3D-Magic/OmniBot.git
cd OmniBot

# 2. Run automated setup (asks for API keys once)
bash setup.sh

# 3. Start trading
sudo systemctl start omnibot-v2.5.service
```

**That\'s it!** The bot will automatically start trading when the US market opens.

### Option 2: Detailed Installation

If the quick start doesn\'t work, or you want to understand each step:

#### Step 1: Clone Repository
```bash
git clone https://github.com/3D-Magic/OmniBot.git
cd OmniBot
```

#### Step 2: Install System Dependencies
```bash
sudo apt update && sudo apt full-upgrade -y
sudo apt install -y python3-venv python3-pip python3-dev build-essential \
    libopenblas-dev liblapack-dev gfortran postgresql libpq-dev \
    redis-server git vim htop tree tmux sqlite3 libsqlite3-dev \
    pkg-config cmake libhdf5-dev openssl
```

#### Step 3: Setup Database
```bash
# Generate password
openssl rand -base64 32

# Create database
sudo systemctl enable postgresql
sudo systemctl start postgresql
sudo -u postgres psql <<EOF
CREATE USER biqu WITH PASSWORD 'YOUR_DB_PASSWORD_HERE';
CREATE DATABASE omnibot_db OWNER biqu;
GRANT ALL PRIVILEGES ON DATABASE omnibot_db TO biqu;
\q
EOF
```

#### Step 4: Setup Redis
```bash
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

#### Step 5: Run Setup Script
```bash
bash setup.sh
```

This will:
- Create directory structure
- Install Python dependencies
- **Prompt for Alpaca API keys** (only once)
- Create systemd service

## 🔄 Updating

### Regular Update (Preserves API Keys)
```bash
cd ~/OmniBot
git pull
bash update.sh
```

### Weekend Update (Safe when market closed)
```bash
cd ~/OmniBot
git pull
bash weekend_update.sh
```

**Note:** Updates preserve your API keys in `.env`. You will NOT be asked for keys again.

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
# Only if you need to change API keys
nano ~/omnibot/.env
sudo systemctl restart omnibot-v2.5.service
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

Edit `~/omnibot/.env`:
```bash
TRADING_MODE='live'
```

Then restart:
```bash
sudo systemctl restart omnibot-v2.5.service
```

## 📊 Project Structure

```
omnibot/
├── src/
│   ├── config/          # Configuration management
│   ├── data/            # Data clients (Yahoo Finance)
│   ├── database/        # PostgreSQL models
│   ├── ml/              # ML predictor & regime detection
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
├── .env                 # API keys (created by setup.sh)
├── setup.sh             # Initial setup script
├── update.sh            # Update script (preserves keys)
├── weekend_update.sh    # Safe weekend update
├── omnibot-v2.5.service # Systemd service file
└── README.md            # This file
```

## 🔧 Troubleshooting

### Error: "unauthorized" when trading
**Cause:** Invalid Alpaca API keys

**Fix:**
```bash
# Check if keys are set
cat ~/omnibot/.env | grep ALPACA

# If empty or wrong, edit manually
nano ~/omnibot/.env

# Then restart
sudo systemctl restart omnibot-v2.5.service
```

### Error: "ModuleNotFoundError: No module named 'talib'"
**Fix:**
```bash
source ~/omnibot/venv/bin/activate
pip install talib-binary
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
- **Keep your API keys secret** - they provide access to your trading account
- **Use paper trading first** - always test thoroughly before live trading
- **Secure your Raspberry Pi** - use strong passwords and keep it updated
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
- [TA-Lib](https://mrjbq7.github.io/ta-lib/) for technical indicators
- [yfinance](https://github.com/ranaroussi/yfinance) for market data

## ⚠️ Disclaimer

**This software is for educational purposes only. Trading stocks involves substantial risk of loss. Past performance is not indicative of future results. Always use paper trading to test strategies before risking real capital.**

---

**Happy Trading! 🚀**
