#!/bin/bash
# OMNIBOT v3.0 - Update Script
# Updates code but preserves API keys and configuration

echo "=========================================="
echo "OMNIBOT v3.0 - Update"
echo "=========================================="
echo ""

# Check if configured
if [ ! -f ~/omnibot/.env ]; then
    echo "❌ Not configured yet. Run setup.sh first:"
    echo "   bash setup.sh"
    exit 1
fi

# Backup API keys
echo "[1/5] Backing up configuration..."
cp ~/omnibot/.env /tmp/omnibot_env_backup

# Stop service
echo "[2/5] Stopping service..."
sudo systemctl stop omnibot-v2.5.service 2>/dev/null || true

# Update code
echo "[3/5] Updating source code..."
# Copy new src files (assumes running from git repo)
if [ -d "src" ]; then
    cp -r src/* ~/omnibot/src/
else
    echo "⚠ No src directory found. Are you in the git repo?"
    exit 1
fi

# Restore API keys (in case they were overwritten)
echo "[4/5] Restoring configuration..."
if [ -f /tmp/omnibot_env_backup ]; then
    cp /tmp/omnibot_env_backup ~/omnibot/.env
    chmod 600 ~/omnibot/.env
fi

# Restart
echo "[5/5] Restarting service..."
sudo systemctl daemon-reload
sudo systemctl start omnibot-v2.5.service

echo ""
echo "=========================================="
echo "✓ Update Complete!"
echo "=========================================="
echo ""
sudo systemctl status omnibot-v2.5.service --no-pager -l
