# OMNIBOT v2.5 - Post-SD Card Setup Guide

This guide covers everything AFTER your Raspberry Pi SD card is flashed with Raspberry Pi OS.

## ✅ Pre-Flight Checklist (Already Done)

Before using this package, you should have:
- [ ] Raspberry Pi OS (64-bit) installed on SD card
- [ ] SSH enabled
- [ ] Hostname set (e.g., "omnibot")
- [ ] User account created
- [ ] Pi connected to network (Ethernet or WiFi)
- [ ] You can SSH into the Pi

## 🚀 Step-by-Step Setup

### Step 1: SSH into Raspberry Pi

From your computer:

```bash
# Using hostname (if mDNS is working)
ssh omnibot@omnibot.local

# Or using IP address (find via router or Angry IP Scanner)
ssh omnibot@192.168.1.xxx
```

**Default credentials** (if you didn't change them):
- Username: `pi` or what you set during imaging
- Password: what you set during imaging

### Step 2: Download OMNIBOT

Once logged into the Pi:

```bash
# Update package lists first
sudo apt update

# Install git if not present
sudo apt install -y git

# Clone the repository
git clone https://github.com/yourusername/omnibot-v2.5.git

# Enter directory
cd omnibot-v2.5
```

### Step 3: Run Automated Setup

```bash
# Make setup executable and run
chmod +x setup.sh
./setup.sh
```

**What setup.sh does:**
1. Updates system packages (`apt update && apt upgrade`)
2. Installs system dependencies (PostgreSQL, Redis, build tools)
3. Creates PostgreSQL database with random secure password
4. Sets up Redis for caching
5. Creates Python virtual environment
6. Installs PyTorch (CPU version for Pi)
7. Installs all Python requirements
8. Downloads NLTK data for NLP
9. Creates directory structure
10. Generates initial `.env` file

**⏱️ Time required:** 30-60 minutes depending on Pi model and internet speed

**💾 Disk space:** ~2-3 GB for all dependencies

### Step 4: Configure API Keys

You need API keys from Alpaca Markets (free for paper trading):

1. Go to https://alpaca.markets
2. Create free account
3. Go to "Paper Trading" section
4. Generate API Keys
5. Copy Key ID and Secret Key

Then run:

```bash
python src/main.py --setup
```

Enter your keys when prompted. This creates the `.env` file.

### Step 5: Verify Installation

```bash
# Test database connection
python src/main.py --trades

# Expected output:
# "No trades found in the specified period."
# (This is normal - no trades yet!)
```

### Step 6: Start Trading

**Option A: Manual Mode (testing)**

```bash
python src/main.py --mode cli
```

You'll see:
- Engine initialization
- Mode: PAPER
- Trading loop starting

Press `Ctrl+C` to stop.

**Option B: Service Mode (24/7 operation)**

```bash
# Install systemd service
sudo ./scripts/install-service.sh

# Start the service
sudo systemctl start omnibot

# Check it's running
sudo systemctl status omnibot
```

## 📊 Daily Operations

### Viewing Logs

```bash
# Live logs (follow mode)
sudo journalctl -u omnibot -f

# Last 100 lines
sudo journalctl -u omnibot -n 100

# Today's logs only
sudo journalctl -u omnibot --since today

# Search for errors
sudo journalctl -u omnibot | grep -i error
```

### Checking Trades

```bash
# Recent trades (last 2 days)
python src/main.py --trades

# Last week
python src/main.py --trades --days 7

# Specific symbol
python src/main.py --trades --symbol TSLA

# Export to CSV
python src/main.py --trades --export trades.csv
```

### Service Management

```bash
# Check status
sudo systemctl status omnibot

# Control service
sudo systemctl start omnibot    # Start
sudo systemctl stop omnibot     # Stop
sudo systemctl restart omnibot  # Restart

# Enable/disable auto-start
sudo systemctl enable omnibot   # Start on boot
sudo systemctl disable omnibot  # Don't start on boot
```

## 🔧 Configuration

### Trading Parameters

Edit `src/config/settings.py`:

```python
class TradingConfig:
    max_position_pct = 0.15      # Max 15% per position
    symbols = ['TQQQ', 'TSLA']   # Assets to trade
    max_daily_trades = 50        # Limit trades per day
    scan_interval = 10           # Seconds between scans
    market_open_only = True      # Only trade market hours
```

### Switching to Live Trading

**⚠️ DANGER: Only after extensive paper testing!**

1. Stop the bot: `sudo systemctl stop omnibot`
2. Edit `.env`: Change `TRADING_MODE='paper'` to `TRADING_MODE='live'`
3. Get LIVE API keys from Alpaca (different from paper keys!)
4. Update API keys: `python src/main.py --setup`
5. Start bot: `sudo systemctl start omnibot`

## 🐛 Troubleshooting

### Setup Issues

**"setup.sh: Permission denied"**
```bash
chmod +x setup.sh
./setup.sh
```

**"apt lock" errors during setup**
```bash
# Wait a few minutes and retry
# Or check what's locking:
sudo lsof /var/lib/dpkg/lock-frontend
```

**Out of memory during PyTorch install**
```bash
# Increase swap temporarily
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
# Then re-run setup
```

### Runtime Issues

**"ModuleNotFoundError"**
```bash
source venv/bin/activate
pip install <missing-module-name>
sudo systemctl restart omnibot
```

**Database connection failed**
```bash
# Check PostgreSQL
sudo systemctl status postgresql

# Or use SQLite instead (edit .env)
DATABASE_URL='sqlite:///omnibot.db'
```

**Service fails to start**
```bash
# Check logs for specific error
sudo journalctl -u omnibot -n 50

# Common fixes:
sudo chown -R omnibot:omnibot ~/omnibot-v2.5
chmod 600 .env
```

**Slow performance**
```bash
# Check temperature (should be < 80°C)
vcgencmd measure_temp

# Check CPU usage
htop

# Reduce symbols in config if needed
```

## 💾 Backup & Restore

### Backup

```bash
# Create backup directory
mkdir -p ~/backups

# Backup database
sudo -u postgres pg_dump omnibot_db > ~/backups/omnibot-db-$(date +%Y%m%d).sql

# Backup config
cp .env ~/backups/env-$(date +%Y%m%d)

# Backup models
tar -czf ~/backups/models-$(date +%Y%m%d).tar.gz models/
```

### Restore

```bash
# Restore database
sudo -u postgres psql omnibot_db < ~/backups/omnibot-db-YYYYMMDD.sql

# Restore config
cp ~/backups/env-YYYYMMDD .env

# Restart
sudo systemctl restart omnibot
```

## 🔒 Security

1. **Change default password** if not done:
   ```bash
   passwd
   ```

2. **Secure .env file** (should already be 600):
   ```bash
   chmod 600 .env
   ```

3. **Enable firewall**:
   ```bash
   sudo apt install ufw
   sudo ufw allow ssh
   sudo ufw enable
   ```

4. **Keep updated**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

## 📈 Performance Tips

- **Use SSD** instead of SD card for better I/O
- **Ethernet** instead of WiFi for stability
- **Disable Bluetooth** if not needed:
  ```bash
  sudo systemctl disable bluetooth
  ```
- **Monitor temperature**: `watch -n 5 vcgencmd measure_temp`

## ✅ Success Indicators

You'll know it's working when:
- [ ] `python src/main.py --trades` shows no errors
- [ ] Logs show "TRADING LOOP STARTED"
- [ ] Alpaca dashboard shows connection
- [ ] No errors in `sudo journalctl -u omnibot`

## 🆘 Getting Help

If stuck:
1. Check logs: `sudo journalctl -u omnibot -n 100`
2. Verify Python: `python3 --version` (should be 3.9+)
3. Check disk space: `df -h`
4. Check memory: `free -h`

Open GitHub issue with logs and system info.

---

**Your OMNIBOT should now be trading! 🚀**
