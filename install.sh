#!/bin/bash
# OMNIBOT v2.5 - One-Command Installer
# Usage: curl -sSL https://raw.githubusercontent.com/3D-Magic/OmniBot/main/install.sh | bash

set -e

echo "=========================================="
echo "OMNIBOT v2.5 - Automated Installer"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Raspberry Pi
if [[ $(uname -m) != "aarch64" && $(uname -m) != "armv7l" ]]; then
    echo -e "${YELLOW}Warning: This doesn't appear to be a Raspberry Pi${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get API Keys from user
echo ""
echo "=========================================="
echo "API KEY CONFIGURATION"
echo "=========================================="
echo ""
echo "Get your FREE paper trading keys from:"
echo "https://alpaca.markets"
echo ""

read -p "Alpaca API Key: " ALPACA_KEY
read -p "Alpaca Secret Key: " ALPACA_SECRET
read -p "NewsAPI Key (optional, press Enter to skip): " NEWSAPI_KEY

# Validate inputs
if [ -z "$ALPACA_KEY" ] || [ -z "$ALPACA_SECRET" ]; then
    echo -e "${RED}Error: Alpaca API keys are required${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo "DATABASE CONFIGURATION"
echo "=========================================="
echo ""
echo "Choose database:"
echo "1) PostgreSQL (recommended for production)"
echo "2) SQLite (easier, no setup required)"
read -p "Enter choice (1 or 2): " DB_CHOICE

if [ "$DB_CHOICE" = "1" ]; then
    DB_TYPE="postgresql"
    echo ""
    echo "PostgreSQL will be installed automatically."
    read -p "Create database password (or press Enter for auto-generated): " DB_PASS
    if [ -z "$DB_PASS" ]; then
        DB_PASS=$(openssl rand -base64 32)
        echo "Auto-generated password: $DB_PASS"
    fi
else
    DB_TYPE="sqlite"
    DB_PASS=""
    echo "Using SQLite (no password needed)"
fi

echo ""
echo "=========================================="
echo "INSTALLING OMNIBOT v2.5"
echo "=========================================="
echo ""

# Update system
echo "→ Updating system packages..."
sudo apt update && sudo apt full-upgrade -y

# Install system dependencies
echo "→ Installing system dependencies..."
sudo apt install -y python3-venv python3-pip python3-dev build-essential \
    libopenblas-dev liblapack-dev gfortran postgresql libpq-dev \
    redis-server git vim htop tree tmux sqlite3 libsqlite3-dev \
    pkg-config cmake libhdf5-dev openssl

# Setup database
if [ "$DB_TYPE" = "postgresql" ]; then
    echo "→ Setting up PostgreSQL..."
    sudo systemctl enable postgresql
    sudo systemctl start postgresql

    # Create user and database
    sudo -u postgres psql -c "CREATE USER omnibot WITH PASSWORD '$DB_PASS';" 2>/dev/null || true
    sudo -u postgres psql -c "CREATE DATABASE omnibot_db OWNER omnibot;" 2>/dev/null || true
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE omnibot_db TO omnibot;"

    DB_URL="postgresql://omnibot:$DB_PASS@localhost:5432/omnibot_db"
else
    DB_URL="sqlite:///omnibot.db"
fi

# Setup Redis
echo "→ Setting up Redis..."
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Create project directory
INSTALL_DIR="$HOME/OmniBot"
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}→ Directory exists, updating...${NC}"
    cd "$INSTALL_DIR"
    git pull origin main 2>/dev/null || true
else
    echo "→ Downloading OMNIBOT..."
    git clone https://github.com/3D-Magic/OmniBot.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# Create virtual environment
echo "→ Creating Python environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "→ Installing Python packages..."
pip install --upgrade pip setuptools wheel

# Install PyTorch (CPU version for Pi)
echo "→ Installing PyTorch (this takes 10-15 minutes)..."
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install requirements
echo "→ Installing dependencies..."
pip install -r requirements.txt

# Download NLTK data
echo "→ Downloading NLP data..."
python -m nltk.downloader punkt vader_lexicon stopwords wordnet

# Create directories
echo "→ Creating directories..."
mkdir -p models data logs backups secrets

# Create .env file with user-provided keys
echo "→ Creating configuration..."
cat > .env << EOF
# OMNIBOT v2.5 Configuration
# Generated: $(date -Iseconds)

ALPACA_API_KEY_ENC='$ALPACA_KEY'
ALPACA_SECRET_KEY_ENC='$ALPACA_SECRET'
NEWSAPI_KEY_ENC='$NEWSAPI_KEY'
POLYGON_KEY_ENC=''

DATABASE_URL='$DB_URL'
REDIS_URL='redis://localhost:6379/0'
TRADING_MODE='paper'

MODEL_PATH='./models'
DATA_PATH='./data'
EOF

chmod 600 .env

# Summary
echo ""
echo "=========================================="
echo -e "${GREEN}✓ INSTALLATION COMPLETE!${NC}"
echo "=========================================="
echo ""
echo "Installation directory: $INSTALL_DIR"
echo ""
echo "Next steps:"
echo ""
echo "1. Start paper trading:"
echo "   python src/main.py --mode cli"
echo ""
echo "2. Or install as service (runs 24/7):"
echo "   sudo ./scripts/install-service.sh"
echo "   sudo systemctl start omnibot"
echo ""
echo "3. View trades:"
echo "   python src/main.py --trades"
echo ""
echo "4. View logs:"
echo "   sudo journalctl -u omnibot -f"
echo ""
echo "=========================================="
echo "IMPORTANT:"
echo "- Trading in PAPER mode (safe for testing)"
echo "- Edit .env to switch to LIVE mode (DANGEROUS!)"
echo "- API keys stored securely in .env"
echo "=========================================="
