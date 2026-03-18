#!/bin/bash
echo "=========================================="
echo "OMNIBOT v2.5.1 - Multi-Market Setup"
echo "=========================================="

if [ -f /home/biqu/omnibot/.env ]; then
    echo "✓ Already configured"
    echo "Start: sudo systemctl start omnibot-v2.5.service"
    exit 0
fi

echo "[1/4] Creating directories..."
mkdir -p /home/biqu/omnibot/{src/{config,data,database,ml,risk,trading,utils,gui,tests},logs,backups}

echo "[2/4] Setting up Python..."
cd /home/biqu/omnibot
python3 -m venv venv 2>/dev/null || true
source venv/bin/activate
pip install --upgrade pip -q
pip install -q alpaca-py pandas numpy yfinance sqlalchemy psycopg2-binary pydantic-settings talib-binary pytz redis python-dotenv

echo ""
echo "[3/4] API Keys (from https://app.alpaca.markets/)"
read -p "Alpaca API Key: " alpaca_key
read -p "Alpaca Secret Key: " alpaca_secret

db_pass=$(openssl rand -base64 16 | tr -dc 'a-zA-Z0-9' | head -c 16)

echo "[4/4] Creating config..."
cat > /home/biqu/omnibot/.env << EOF
ALPACA_API_KEY_ENC='${alpaca_key}'
ALPACA_SECRET_KEY_ENC='${alpaca_secret}'
DATABASE_URL='sqlite:///omnibot.db'
TRADING_MODE='paper'
EOF
chmod 600 /home/biqu/omnibot/.env

echo "Installing service..."
sudo tee /etc/systemd/system/omnibot-v2.5.service > /dev/null << 'EOF'
[Unit]
Description=OMNIBOT v2.5.1 Multi-Market
After=network.target
[Service]
Type=simple
User=biqu
WorkingDirectory=/home/biqu/omnibot/src
Environment="PYTHONPATH=/home/biqu/omnibot/src"
EnvironmentFile=/home/biqu/omnibot/.env
ExecStart=/home/biqu/omnibot/venv/bin/python /home/biqu/omnibot/src/main.py
Restart=always
[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable omnibot-v2.5.service

echo ""
echo "✓ Setup complete!"
echo "Start: sudo systemctl start omnibot-v2.5.service"
echo "Logs:  sudo journalctl -u omnibot-v2.5.service -f"
