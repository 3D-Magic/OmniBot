# 🤖 OMNIBOT v2.5 - Raspberry Pi Trading Bot

> **ML-Enhanced Trading System for Raspberry Pi**  
> **PROTECTED - Personal Use License**

**⚠️ LICENSE NOTICE:**
This software is FREE for personal use only. 
- ✅ Use for your own trading
- ❌ NO selling
- ❌ NO modifications  
- ❌ NO redistribution
- ❌ NO commercial use
- 🔒 Technical protections active

**📄 For SD card setup instructions, see:** [OmniBot v2.5 Paper Trading Steps.pdf](https://github.com/3D-Magic/OmniBot/releases/download/v2.5/OmniBot.v2.5.Paper.Trading.Steps.pdf)

## ⚡ Quick Start (After SD Card is Ready)

```bash
# 1. SSH into your Raspberry Pi
ssh omnibot@omnibot.local

# 2. Clone this repository
git clone https://github.com/3D-Magic/OmniBot.git
cd OmniBot

# 3. Run setup
chmod +x setup.sh
./setup.sh

# 4. Configure API keys (requires admin password)
python src/main.py --setup

# 5. Start trading
python src/main.py --mode cli
```

## 🔒 Security Features

This protected version includes:
- **File Integrity Verification** - Bot won't start if code is modified
- **Admin Password Protection** - Required for configuration changes
- **License Watermarks** - Embedded in all outputs
- **Tamper Detection** - Automatic violation detection

**Admin Password:** Required for setup (contact administrator)

## 📋 Prerequisites

- Raspberry Pi OS installed on SD card
- SSH enabled
- Network connectivity
- See PDF above for SD card setup

**Hardware:**
- Raspberry Pi 4 (4GB or 8GB RAM)
- MicroSD Card (32GB+, Class 10)
- Power supply
- Internet connection

## 🚀 Installation

See PDF guide for detailed SD card setup. After that:

```bash
git clone https://github.com/3D-Magic/OmniBot.git
cd OmniBot
./setup.sh
```

## 📊 Usage

```bash
# Start trading
python src/main.py --mode cli

# View trades
python src/main.py --trades

# Run as service
sudo ./scripts/install-service.sh
sudo systemctl start omnibot
```

## ⚠️ License Reminder

By using this software, you agree to:
- Use ONLY for personal trading
- NOT sell, modify, or redistribute
- Accept all trading risks

See LICENSE file for complete terms.

---

**Ready to trade! 🚀**
