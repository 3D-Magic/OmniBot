#!/bin/bash
# OmniBot v2.6.1 Sentinel - Setup Script

set -e

echo "🤖 OmniBot v2.6.1 Sentinel - Setup"
echo "================================"

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "📍 Python version: $PYTHON_VERSION"

REQUIRED_VERSION="3.8"
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    echo "❌ Python 3.8+ required"
    exit 1
fi

echo "📦 Installing system dependencies..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y -qq tmux wget unzip curl git
elif command -v yum &> /dev/null; then
    sudo yum install -y tmux wget unzip curl git
fi

echo "📦 Installing Python packages..."
pip3 install -q flask flask-cors numpy pandas requests pyyaml scikit-learn

if ! command -v ngrok &> /dev/null; then
    echo "📦 Installing ngrok..."
    ARCH=$(uname -m)
    if [[ "$ARCH" == "aarch64" ]] || [[ "$ARCH" == "arm64" ]]; then
        NGROK_URL="https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm64.tgz"
    elif [[ "$ARCH" == "armv7l" ]]; then
        NGROK_URL="https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm.tgz"
    else
        NGROK_URL="https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz"
    fi

    wget -q "$NGROK_URL" -O /tmp/ngrok.tgz
    sudo tar -xzf /tmp/ngrok.tgz -C /usr/local/bin
    rm /tmp/ngrok.tgz

    echo "✅ ngrok installed"
    echo "⚠️  Run: ngrok config add-authtoken <YOUR_TOKEN>"
    echo "   Get token at: https://dashboard.ngrok.com"
fi

mkdir -p logs data backups config
chmod +x scripts/omnibot.sh

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Configure ngrok: ngrok config add-authtoken <TOKEN>"
echo "  2. Start bot: ./scripts/omnibot.sh start --ngrok"
echo "  3. View dashboard: http://localhost:8081"
