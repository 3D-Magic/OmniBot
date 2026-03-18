#!/bin/bash
# OMNIBOT v2.5.1 - Initial Setup Script
# Asks for API keys once, never again

echo "=========================================="
echo "OMNIBOT v2.5.1 - Initial Setup"
echo "=========================================="
echo ""

# Check if already configured
if [ -f /home/biqu/omnibot/.env ]; then
    echo "✓ Already configured (.env exists at /home/biqu/omnibot/.env)"
    echo ""
    echo "To reconfigure (will overwrite API keys):"
    echo "  rm /home/biqu/omnibot/.env"
    echo "  bash setup.sh"
    echo ""
    echo "To start trading:"
    echo "  sudo systemctl start omnibot-v2.5.service"
    exit 0
fi

echo "This setup will:"
echo "  1. Create directory structure"
echo "  2. Install Python dependencies"
echo "  3. Ask for Alpaca API keys (ONE TIME ONLY)"
echo "  4. Configure systemd service"
echo "  5. Enable auto-updates"
echo ""
read -p "Press Enter to continue..."
echo ""

# Step 1: Create directories
echo "[1/5] Creating directory structure..."
mkdir -p /home/biqu/omnibot/{src/{config,data,database,ml,risk,trading,utils,gui,tests},logs,data,secrets,models,backups}

# Step 2: Python environment
echo "[2/5] Setting up Python environment..."
cd /home/biqu/omnibot

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip -q

# Install dependencies
pip install alpaca-py pandas numpy yfinance sqlalchemy psycopg2-binary pydantic-settings talib-binary redis python-dotenv -q

if [ $? -ne 0 ]; then
    echo "⚠ Some packages failed, trying alternative..."
    pip install TA-Lib -q || pip install talib-binary -q
fi

echo ""
echo "[3/5] API Key Configuration"
echo "----------------------------------------"
echo "Get your API keys from: https://app.alpaca.markets/"
echo "(Paper trading keys recommended for testing)"
echo ""

# Prompt for keys
read -p "Alpaca API Key: " alpaca_key
read -p "Alpaca Secret Key: " alpaca_secret

# Generate DB password
db_pass=$(openssl rand -base64 16 | tr -dc 'a-zA-Z0-9' | head -c 16)

echo ""
echo "[4/5] Creating configuration..."

# Create .env file
cat > /home/biqu/omnibot/.env << EOF
# OMNIBOT v2.5.1 Configuration
# Generated: $(date -Iseconds)
# THIS FILE IS PRESERVED DURING AUTO-UPDATES

# API Keys (from setup.sh)
ALPACA_API_KEY_ENC='${alpaca_key}'
ALPACA_SECRET_KEY_ENC='${alpaca_secret}'
NEWSAPI_KEY_ENC=''
POLYGON_KEY_ENC=''

# Database
DATABASE_URL='postgresql://biqu:${db_pass}@localhost:5432/omnibot_db'
REDIS_URL='redis://localhost:6379/0'

# Trading Mode (paper/live)
TRADING_MODE='paper'

# Paths
MODEL_PATH='/home/biqu/omnibot/models'
DATA_PATH='/home/biqu/omnibot/data'
EOF

chmod 600 /home/biqu/omnibot/.env
chown biqu:biqu /home/biqu/omnibot/.env

echo "✓ Configuration saved to /home/biqu/omnibot/.env"
echo "  (This file will NEVER be overwritten by updates)"
echo ""

# Step 5: Setup systemd service
echo "[5/5] Installing systemd service..."

sudo tee /etc/systemd/system/omnibot-v2.5.service > /dev/null << 'EOF'
[Unit]
Description=OMNIBOT v2.5.1 Intelligent Trading System
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=simple
User=biqu
Group=biqu
WorkingDirectory=/home/biqu/omnibot/src
Environment="PYTHONPATH=/home/biqu/omnibot/src"
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/home/biqu/omnibot/.env
ExecStart=/home/biqu/omnibot/venv/bin/python /home/biqu/omnibot/src/main.py
ExecStop=/bin/kill -SIGINT $MAINPID
Restart=always
RestartSec=10
StartLimitInterval=60s
StartLimitBurst=3

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable omnibot-v2.5.service

echo ""
echo "=========================================="
echo "✓ Setup Complete!"
echo "=========================================="
echo ""
echo "Your API keys are saved and will be preserved"
echo "during all future automatic updates."
echo ""
echo "Start trading:"
echo "  sudo systemctl start omnibot-v2.5.service"
echo ""
echo "View logs:"
echo "  sudo journalctl -u omnibot-v2.5.service -f"
echo ""
echo "Check trades:"
echo "  cd /home/biqu/omnibot && python src/main.py --trades"
echo ""
echo "The bot will automatically update itself on weekends"
echo "when the market is closed. No action required!"
echo ""
