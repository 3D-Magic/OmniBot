## OmniBot v2.6.1 Sentinel

**ML-Enhanced Automated Trading System with Aggressive Trading Modes & Auto-Updates**

A trading bot designed for automated stock trading—no market expertise required. Built to help anyone generate passive income and work toward financial freedom through intelligent, hands-free investing.

**US Stocks | Asia Stocks | Forex**

Multi-market algorithmic trading bot for Raspberry Pi 4.

---

### Supported Markets

| Market | Hours (NZDT) | Status |
|--------|--------------|--------|
| 🇺🇸 US Stocks | 3:30 AM - 10:00 AM | ✅ |
| 🇯🇵 Japan | 1:00 PM - 7:00 PM | ✅ |
| 🇭🇰 Hong Kong | 1:30 PM - 8:00 PM | ✅ |
| 🇸🇬 Singapore | 1:00 PM - 9:00 PM | Optional |
| 💱 Forex | 24/5 Mon-Fri | ✅ |

---

### Quick Start

```bash
git clone https://github.com/3D-Magic/OmniBot.git
cd OmniBot
bash setup.sh
sudo systemctl start omnibot-v2.6.service
```

---

### Enable/Disable Markets

Edit `src/config/settings.py`:

```python
enable_us: bool = True
enable_japan: bool = True
enable_hongkong: bool = True
enable_singapore: bool = False
enable_forex: bool = True
```

---

### 🛠️ Commands

| Command | Description |
|---------|-------------|
| `./omnibot.sh start` | Start bot with ngrok |
| `./omnibot.sh stop` | Stop bot |
| `./omnibot.sh restart` | Restart bot |
| `./omnibot.sh url` | Get current ngrok URL |
| `./omnibot.sh status` | Check if running |

---

### 📊 Features

- **Trading Modes**: Conservative, Moderate, Aggressive, HFT Scalper, Sentinel
- **Auto-Update**: Weekend automatic updates (no manual intervention required)
- **Dashboard**: Web interface with mode selector
- **Update/Restart Buttons**: One-click operations
- **API Endpoints**: `/api/positions`, `/api/portfolio`, `/api/strategies`, `/api/system`, `/api/history`

---

## 🆕 Improvements from v2.5.1 to v2.6.1 Sentinel

**Note**: The version jump from v2.5.1 to v2.6.1 reflects critical staged fixes that have been thoroughly tested and validated. **v2.6.1 Sentinel is now the current most stable release** and has graduated from the testing environment to become the production-ready standard.

| Feature | v2.5.1 | v2.6.1 Sentinel |
|---------|--------|-----------------|
| **Trading Modes** | Basic preset modes | 5 distinct modes: Conservative, Moderate, Aggressive, HFT Scalper, Sentinel |
| **Auto-Updates** | ❌ Manual updates required | ✅ **Fully automated weekend updates** — bot checks for updates when markets are closed and applies them automatically with zero user intervention |
| **Update Mechanism** | Manual git pull + restart | Built-in update scheduler with automatic restart |
| **Dashboard** | Basic web view | Enhanced dashboard with live mode selector and control buttons |
| **Control Interface** | CLI only | Web-based Update/Restart buttons for one-click operations |
| **API Endpoints** | Limited | Expanded API: positions, portfolio, strategies, system status, trade history |
| **Branch Management** | Single branch | Dedicated stable release branch with staged fix integration |
| **Stability** | Standard | **Production-stable** — all critical fixes pre-validated in testing environment |

---

### 🔑 Key Upgrade Benefits

1. **Zero-Maintenance Operation**: Set and forget — the bot handles its own updates during weekend market downtime
2. **Risk Flexibility**: Instantly switch between conservative wealth preservation and aggressive growth strategies
3. **Remote Management**: Control your bot from anywhere via the web dashboard
4. **Production Ready**: v2.6.1 has completed the full testing cycle and is now the recommended stable release

---

### License

Personal Use License - See LICENSE file
