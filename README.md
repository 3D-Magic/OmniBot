# 🤖 OMNIBOT v2.5 - Raspberry Pi Trading Bot

> **ML-Enhanced Trading System for Raspberry Pi**  
> **One-command installation with interactive setup**

## ⚡ Quick Install (One Command)

After your Raspberry Pi SD card is flashed and you can SSH in, run:

```bash
curl -sSL https://raw.githubusercontent.com/3D-Magic/OmniBot/main/install.sh | bash
```

This single command will:
- ✅ Prompt for your Alpaca API keys
- ✅ Ask for database preference (PostgreSQL or SQLite)
- ✅ Install all system dependencies
- ✅ Setup database with secure password
- ✅ Create Python virtual environment
- ✅ Install PyTorch and ML libraries
- ✅ Configure everything automatically

**Then just start trading:**
```bash
cd ~/OmniBot
python src/main.py --mode cli
```

---

## 📋 Prerequisites

Before running the install command:
- ✅ Raspberry Pi OS (64-bit) installed on SD card
- ✅ SSH enabled
- ✅ Network connected (Ethernet or WiFi)
- ✅ You can SSH into the Pi

**Hardware:**
- Raspberry Pi 4 (4GB or 8GB RAM recommended)
- MicroSD Card (32GB+, Class 10)
- Power supply
- Internet connection

---

## 🔑 What You'll Need During Install

The installer will prompt you for:

1. **Alpaca API Key** (from [alpaca.markets](https://alpaca.markets))
   - Create free account → "Paper Trading" → "Generate API Keys"

2. **Alpaca Secret Key**
   - Shown alongside API key

3. **NewsAPI Key** (optional)
   - Get free key at [newsapi.org](https://newsapi.org)
   - Press Enter to skip

4. **Database Choice**
   - Option 1: PostgreSQL (better for production)
   - Option 2: SQLite (easier, no setup)

---

## 🚀 What Happens During Install

```
Step 1: Update system packages
Step 2: Install PostgreSQL & Redis (if chosen)
Step 3: Create database with secure password
Step 4: Download OMNIBOT from GitHub
Step 5: Create Python virtual environment
Step 6: Install PyTorch (10-15 min)
Step 7: Install all Python dependencies
Step 8: Download NLP data
Step 9: Create .env file with your API keys
Step 10: Ready to trade!
```

**⏱️ Total time: 30-60 minutes**

---

## 📊 Using OMNIBOT

### Start Trading
```bash
# Manual mode
python src/main.py --mode cli

# Or as service (24/7)
sudo ./scripts/install-service.sh
sudo systemctl start omnibot
```

### View Trades
```bash
python src/main.py --trades              # Recent trades
python src/main.py --trades --days 7     # Last 7 days
python src/main.py --trades --export csv # Export to CSV
```

### Monitor Logs
```bash
sudo journalctl -u omnibot -f            # Live logs
sudo systemctl status omnibot            # Check status
```

---

## 📁 Project Structure

```
~/OmniBot/
├── src/
│   ├── config/          # Configuration management
│   ├── database/        # Trade database & analytics
│   ├── ml/              # LSTM predictor & regime detection
│   ├── risk/            # Risk management
│   ├── trading/         # Trading engine
│   └── main.py          # Entry point
├── scripts/
│   └── install-service.sh  # Systemd service installer
├── setup.sh             # Manual setup script
├── install.sh           # One-command installer
├── requirements.txt     # Python dependencies
└── .env                 # Your API keys (auto-created)
```

---

## 🔧 Configuration

### Edit Trading Parameters
```bash
nano src/config/settings.py
```

Change:
- `symbols` - Which stocks to trade
- `max_position_pct` - Max portfolio % per trade
- `scan_interval` - Seconds between market scans

### Switch to Live Trading
**⚠️ DANGER: Only after extensive paper testing!**

1. Stop bot: `sudo systemctl stop omnibot`
2. Edit `.env`: Change `TRADING_MODE='paper'` to `TRADING_MODE='live'`
3. Get LIVE API keys from Alpaca (different from paper!)
4. Update keys: Edit `.env` file
5. Restart: `sudo systemctl start omnibot`

---

## 🐛 Troubleshooting

**"Permission denied"**
```bash
chmod +x install.sh
./install.sh
```

**"Module not found"**
```bash
source venv/bin/activate
pip install <missing-module>
```

**Database connection error**
```bash
# Edit .env to use SQLite instead
nano .env
# Change: DATABASE_URL='sqlite:///omnibot.db'
```

**Service won't start**
```bash
# Check logs
sudo journalctl -u omnibot -n 50

# Fix permissions
chmod 600 .env
sudo chown -R $USER:$USER ~/OmniBot
```

---

## ⚠️ Safety First

- ✅ **Starts in PAPER mode** (safe for testing)
- ✅ **Test for weeks** before considering live trading
- ✅ **Never risk money** you can't afford to lose
- ✅ **Keep API keys secret** (`.env` file is protected)
- ✅ **Monitor logs regularly** with `sudo journalctl -u omnibot -f`

---

## 📚 Quick Commands

| Command | Description |
|---------|-------------|
| `python src/main.py --setup` | Reconfigure API keys |
| `python src/main.py --mode cli` | Start trading manually |
| `python src/main.py --trades` | View trade history |
| `sudo systemctl start omnibot` | Start service |
| `sudo systemctl stop omnibot` | Stop service |
| `sudo journalctl -u omnibot -f` | View live logs |

---

## 🤝 Support

Open an issue on GitHub with:
- Error messages from `sudo journalctl -u omnibot -n 50`
- Output of `uname -a`
- Python version: `python3 --version`

---

**Ready to trade! 🚀**

For detailed documentation, see [SETUP_GUIDE.md](SETUP_GUIDE.md)
