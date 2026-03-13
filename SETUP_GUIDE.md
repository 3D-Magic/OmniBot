# OMNIBOT v2.5 - Detailed Setup Guide

## Installation Methods

### Method 1: One-Command Install (Recommended)

```bash
curl -sSL https://raw.githubusercontent.com/3D-Magic/OmniBot/main/install.sh | bash
```

This interactive installer will prompt you for:
- Alpaca API Key
- Alpaca Secret Key  
- NewsAPI Key (optional)
- Database preference (PostgreSQL vs SQLite)

### Method 2: Manual Install

See README.md for step-by-step manual installation.

## Post-Installation

### Test the Installation

```bash
cd ~/OmniBot
python src/main.py --trades
```

Should show: "No trades found in the specified period." (This is normal!)

### Start Trading

**Manual mode:**
```bash
python src/main.py --mode cli
```

**Service mode (24/7):**
```bash
sudo ./scripts/install-service.sh
sudo systemctl start omnibot
```

## Troubleshooting

See README.md troubleshooting section for common issues.
