# OmniBot v2.5.1 - Multi-Market Trading

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: Personal Use](https://img.shields.io/badge/License-Personal%20Use-orange.svg)](#license)

**US Stocks | Asia Stocks | Forex**

Multi-market algorithmic trading bot for Raspberry Pi 4.

## Supported Markets

| Market | Hours (NZDT) | Status |
|--------|-------------|--------|
| 🇺🇸 US Stocks | 3:30 AM - 10:00 AM | ✅ |
| 🇯🇵 Japan | 1:00 PM - 7:00 PM | ✅ |
| 🇭🇰 Hong Kong | 1:30 PM - 8:00 PM | ✅ |
| 🇸🇬 Singapore | 1:00 PM - 9:00 PM | Optional |
| 💱 Forex | 24/5 Mon-Fri | ✅ |

## Quick Start

```bash
git clone https://github.com/3D-Magic/OmniBot.git
cd OmniBot
bash setup.sh
sudo systemctl start omnibot-v2.5.service
```

## Enable/Disable Markets

Edit `src/config/settings.py`:

```python
enable_us: bool = True
enable_japan: bool = True
enable_hongkong: bool = True
enable_singapore: bool = False
enable_forex: bool = True
```

## License

Personal Use License - See LICENSE file
