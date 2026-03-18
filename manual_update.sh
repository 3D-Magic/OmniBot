#!/bin/bash
# OMNIBOT v2.5.1 - Manual Update (Optional)
# Only use this if you want to force an update immediately

echo "=========================================="
echo "OMNIBOT v2.5.1 - Manual Update"
echo "=========================================="
echo ""

# Check if running as root for sudo
if [ "$EUID" -ne 0 ]; then 
    echo "Note: You may be prompted for sudo password"
fi

echo "This will:"
echo "  1. Stop the trading bot"
echo "  2. Pull latest code from GitHub"
echo "  3. Preserve your API keys"
echo "  4. Restart the bot"
echo ""
read -p "Continue? (y/N): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Cancelled"
    exit 0
fi

echo ""
echo "[1/4] Stopping service..."
sudo systemctl stop omnibot-v2.5.service

echo "[2/4] Backing up API keys..."
if [ -f /home/biqu/omnibot/.env ]; then
    cp /home/biqu/omnibot/.env /tmp/omnibot_env_backup
    echo "  ✓ Backed up"
fi

echo "[3/4] Updating code..."
cd /home/biqu/omnibot
git pull origin main

# Restore keys if overwritten
if [ -f /tmp/omnibot_env_backup ]; then
    cp /tmp/omnibot_env_backup /home/biqu/omnibot/.env
    chmod 600 /home/biqu/omnibot/.env
    echo "  ✓ API keys preserved"
fi

echo "[4/4] Restarting service..."
sudo systemctl daemon-reload
sudo systemctl start omnibot-v2.5.service

echo ""
echo "=========================================="
echo "✓ Update Complete!"
echo "=========================================="
echo ""
sudo systemctl status omnibot-v2.5.service --no-pager -l
