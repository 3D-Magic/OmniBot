# OmniBot v2.5.1 - Intelligent Adaptive Trading System

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: Personal Use](https://img.shields.io/badge/License-Personal%20Use-orange.svg)](#license)
[![Alpaca](https://img.shields.io/badge/Alpaca-Paper%20Trading-green.svg)](https://alpaca.markets/)

An ML-enhanced, multi-strategy algorithmic trading bot designed for Raspberry Pi 4, featuring automated weekend updates, RSI-based market signals, and hands-free operation.

## 🚀 Features

- **Automated Weekend Updates**: Bot automatically updates itself when market is closed
- **RSI-Based Trading**: Mean reversion strategy with RSI < 40 entry, RSI > 60 exit
- **Risk Management**: Automatic 3% stop-loss and 6% take-profit
- **Multi-Asset Support**: Trade 13 popular symbols (TQQQ, SOXL, TSLA, NVDA, etc.)
- **Paper Trading**: Test strategies risk-free with Alpaca paper trading
- **24/7 Operation**: Systemd service for automatic startup and monitoring
- **Self-Healing**: Auto-restart on errors, auto-update on weekends

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

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/3D-Magic/OmniBot.git
cd OmniBot

# 2. Run automated setup (asks for API keys once)
bash setup.sh

# 3. Start trading
sudo systemctl start omnibot-v2.5.service
```

**That\'s it!** The bot will:
- Start trading when the US market opens
- **Automatically update itself on weekends**
- Preserve your API keys across updates
- Never require manual intervention

### Detailed Installation

If the quick start doesn\'t work:

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
    pkg-config cmake libhdf5-dev openssl cron
```

#### Step 3: Setup Database
```bash
sudo systemctl enable postgresql
sudo systemctl start postgresql
sudo -u postgres psql <<EOF
CREATE USER biqu WITH PASSWORD 'your_db_password';
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
- **Setup automated weekend updates**

## 🔄 Automated Updates

OmniBot v2.5.1 **automatically updates itself** - no manual steps required!

### How It Works

1. **Bot detects weekend** (Saturday/Sunday or market closed)
2. **Automatically pulls latest code** from GitHub
3. **Preserves API keys** and configuration
4. **Restarts with new code**
5. **Logs all update activity**

### Manual Update (if needed)

```bash
# Only if you want to force an update
bash manual_update.sh
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
│   ├── ml/              # ML predictors
│   ├── risk/            # Risk management
│   ├── trading/         # Main trading engine
│   ├── utils/           # Utilities & auto-updater
│   ├── auto_update.py   # Weekend auto-update module
│   └── main.py          # Entry point
├── logs/                # Log files
├── data/                # Market data cache
├── backups/             # Pre-update backups
├── requirements.txt     # Python dependencies
├── .env                 # API keys (created by setup)
├── setup.sh             # Initial setup (one-time)
├── manual_update.sh     # Force update (optional)
└── README.md            # This file
```

## 🔧 Troubleshooting

### Bot not updating automatically
Check auto-update logs:
```bash
tail -f ~/omnibot/logs/auto_update.log
```

### "unauthorized" when trading
```bash
# Check API keys
cat ~/omnibot/.env | grep ALPACA

# Edit if needed
nano ~/omnibot/.env
sudo systemctl restart omnibot-v2.5.service
```

### Database errors
```bash
sudo systemctl status postgresql
sudo systemctl start postgresql
```

## 🛡️ Security Notes

- **Never commit `.env` file** - it contains your API keys
- **API keys are preserved** during automatic updates
- **Use paper trading first** - always test before live trading
- **Secure your Raspberry Pi** - use strong passwords

## 📈 Performance Expectations

- **Scan Interval**: 10 seconds
- **Update Check**: Every 4 hours during market hours, every 30 mins on weekends
- **Auto-Update**: Only when market closed + new code available
- **Positions**: Max 15% equity per position
- **Risk**: 3% stop loss, 6% take profit

## 📝 License

This project is licensed under the **Personal Use License**.

### What You CAN Do:
- ✅ Use for your own personal trading
- ✅ Modify for your own use
- ✅ Share with friends for their personal use
- ✅ Create backup copies

### What You CANNOT Do:
- ❌ Sell the software
- ❌ Use for commercial trading services
- ❌ Remove copyright notices
- ❌ Use to manage other people\'s money
- ❌ Represent as your own work

See [LICENSE](LICENSE) for full terms.

**For commercial licensing inquiries**, contact: [your-email@example.com]

## ⚠️ Disclaimer

**This software is for educational and personal use only. Trading stocks involves substantial risk of loss. Past performance is not indicative of future results. Always use paper trading to test strategies before risking real capital.**

---

**Happy Trading! 🚀**
