Kimi: I'll display the README content directly here for you to see:

---

# 🤖 OMNIBOT v2.5 - Raspberry Pi Trading Bot

> **ML-Enhanced Trading System for Raspberry Pi**  
> **Run AFTER SD card is flashed with Raspberry Pi OS**

## ⚡ Quick Start (After SD Card is Ready)

```bash
# 1. SSH into your Raspberry Pi (already set up with Pi OS)
ssh omnibot@omnibot.local

# 2. Clone this repository
git clone https://github.com/3D-Magic/OmniBot.git
cd OmniBot

# 3. Run setup (installs everything)
./setup.sh

# 4. Configure API keys
python src/main.py --setup

# 5. Start trading
python src/main.py --mode cli
```

## 📋 Prerequisites (Already Done)

✅ **Raspberry Pi OS installed on SD card**  
✅ **SSH enabled**  
✅ **Network connectivity** (Ethernet or WiFi)  
✅ **You can SSH into the Pi**

**Hardware:**
- Raspberry Pi 4 (4GB or 8GB RAM)
- MicroSD Card (32GB+, Class 10)
- Power supply
- Internet connection

## 🚀 Installation Steps

### Step 1: Connect to Pi

```bash
# Default SSH (if you used 'omnibot' as hostname)
ssh omnibot@omnibot.local

# Or use IP address
ssh omnibot@192.168.1.xxx
```

### Step 2: Download & Setup

```bash
# Download the code
git clone https://github.com/3D-Magic/OmniBot.git
cd OmniBot

# Run automated setup (takes 30-60 minutes)
./setup.sh
```

This will:
- Update system packages
- Install PostgreSQL & Redis
- Create Python virtual environment
- Install PyTorch and all ML libraries
- Download NLP data
- Create database with secure password

### Step 3: Configure API Keys

```bash
python src/main.py --setup
```

Enter:
- **Alpaca API Key** (from [alpaca.markets](https://alpaca.markets))
- **Alpaca Secret Key**
- **NewsAPI Key** (optional)
- Choose PostgreSQL or SQLite

### Step 4: Test

```bash
# Check configuration
python src/main.py --trades

# Should show: "No trades found" (normal for fresh start)
```

### Step 5: Start Trading

**Option A: Run manually**
```bash
python src/main.py --mode cli
```

**Option B: Install as service (runs 24/7)**
```bash
sudo ./scripts/install-service.sh
sudo systemctl start omnibot
```

## 📊 Managing the Bot

### If running as service:

```bash
# View status
sudo systemctl status omnibot

# Start/stop/restart
sudo systemctl start omnibot
sudo systemctl stop omnibot
sudo systemctl restart omnibot

# View logs
sudo journalctl -u omnibot -f

# View last 50 lines
sudo journalctl -u omnibot -n 50
```

### View trades:

```bash
# Recent trades
python src/main.py --trades

# Last 7 days
python src/main.py --trades --days 7

# Export to CSV
python src/main.py --trades --export trades.csv
```

## 📁 Project Structure

```
OmniBot/
├── src/
│   ├── config/          # Configuration management
│   ├── database/        # Trade database & analytics
│   ├── ml/              # LSTM predictor & regime detection
│   ├── risk/            # Risk management
│   ├── trading/         # Trading engine
│   └── main.py          # Entry point
├── scripts/
│   └── install-service.sh  # Systemd installer
├── setup.sh             # Main setup script
├── requirements.txt     # Python dependencies
└── .env                 # Your API keys (created by setup)
```

## 🔧 Configuration

Edit `.env` file:

```bash
# Trading mode
TRADING_MODE='paper'  # paper | live

# Database
DATABASE_URL='postgresql://omnibot:password@localhost:5432/omnibot_db'
# Or use SQLite: 'sqlite:///omnibot.db'

# Symbols (edit src/config/settings.py to change)
```

## 🐛 Troubleshooting

**"Permission denied"**
```bash
chmod +x setup.sh
chmod +x scripts/*.sh
```

**"Module not found"**
```bash
source venv/bin/activate
pip install <missing-module>
```

**Database connection error**
```bash
# Check PostgreSQL
sudo systemctl status postgresql

# Or switch to SQLite (edit .env)
DATABASE_URL='sqlite:///omnibot.db'
```

**Service won't start**
```bash
# Check logs
sudo journalctl -u omnibot -n 50

# Check permissions
ls -la .env  # Should be -rw-------
```

## ⚠️ Safety First

- ✅ **Start with PAPER trading**
- ✅ **Test for weeks before going live**
- ✅ **Never risk money you can't afford to lose**
- ✅ **Keep API keys secret** (never commit .env)
- ✅ **Monitor logs regularly**

## 📚 Documentation

- `commands.sh` - Quick command reference
- Check `src/config/settings.py` for trading parameters
- Alpaca Dashboard: https://app.alpaca.markets/paper/dashboard

## 🤝 Support

Open an issue on GitHub with:
- Error messages from logs
- `uname -a` output
- Python version: `python3 --version`

---

**Ready to trade! 🚀**

---

This matches your original format exactly, with only the git clone steps added!
