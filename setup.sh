#!/bin/bash
# OMNIBOT v3.0 - Initial Setup Script
# Only runs once to configure API keys

echo "=========================================="
echo "OMNIBOT v3.0 - Initial Setup"
echo "=========================================="
echo ""

# Check if already configured
if [ -f ~/omnibot/.env ]; then
    echo "✓ Already configured (.env exists)"
    echo "To reconfigure, delete ~/omnibot/.env and run again"
    exit 0
fi

# Stop service if running
sudo systemctl stop omnibot-v2.5.service 2>/dev/null || true

echo "Step 1/4: Creating directory structure..."
mkdir -p ~/omnibot/{src/{config,data,database,ml,risk,trading,utils,gui,tests},logs,data,secrets,models,backups}

echo "Step 2/4: Checking Python environment..."
cd ~/omnibot
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate

echo "Step 3/4: Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q 2>/dev/null || pip install alpaca-py pandas numpy yfinance sqlalchemy psycopg2-binary pydantic-settings talib-binary -q

echo ""
echo "Step 4/4: API Key Configuration"
echo "----------------------------------------"
echo "Get your API keys from: https://app.alpaca.markets/"
echo ""

read -p "Alpaca API Key: " alpaca_key
read -p "Alpaca Secret Key: " alpaca_secret
read -p "Database Password (or press Enter for auto-generate): " db_pass

# Generate DB password if empty
if [ -z "$db_pass" ]; then
    db_pass=$(openssl rand -base64 16 | tr -dc 'a-zA-Z0-9' | head -c 16)
    echo "Generated DB password: $db_pass"
fi

echo ""
echo "Creating configuration file..."

cat > ~/omnibot/.env << EOF
# OMNIBOT v3.0 Configuration
# Generated: $(date -Iseconds)

# API Keys
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

chmod 600 ~/omnibot/.env

echo "✓ Configuration saved"
echo ""

# Setup systemd service
echo "Installing systemd service..."
sudo tee /etc/systemd/system/omnibot-v2.5.service > /dev/null << 'EOF'
[Unit]
Description=OMNIBOT v3.0 Working Trading System
After=network.target

[Service]
Type=simple
User=biqu
Group=biqu
WorkingDirectory=/home/biqu/omnibot/src
Environment="PYTHONPATH=/home/biqu/omnibot/src"
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/home/biqu/omnibot/.env
ExecStart=/home/biqu/omnibot/venv/bin/python /home/biqu/omnibot/src/main.py
Restart=always
RestartSec=10

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
echo "Start trading: sudo systemctl start omnibot-v2.5.service"
echo "View logs:     sudo journalctl -u omnibot-v2.5.service -f"
echo "Check trades:  cd ~/omnibot && python src/main.py --trades"
echo ""
