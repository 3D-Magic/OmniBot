#!/bin/bash
# OmniBot v2.5 Setup Script for Raspberry Pi

set -e

echo "=================================="
echo "OmniBot v2.5 Setup Script"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "${RED}This script should not be run as root${NC}"
   exit 1
fi

# Update system
echo "${YELLOW}Step 1: Updating system...${NC}"
sudo apt update && sudo apt full-upgrade -y

# Install system dependencies
echo "${YELLOW}Step 2: Installing system dependencies...${NC}"
sudo apt install -y python3-venv python3-pip python3-dev build-essential \
    libopenblas-dev liblapack-dev gfortran postgresql libpq-dev \
    redis-server git vim htop tree tmux sqlite3 libsqlite3-dev \
    pkg-config cmake libhdf5-dev

# Setup PostgreSQL
echo "${YELLOW}Step 3: Setting up PostgreSQL...${NC}"
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Generate random password
DB_PASSWORD=$(openssl rand -base64 32)
echo "Generated database password: $DB_PASSWORD"
echo "${YELLOW}Please save this password!${NC}"

# Create database user and database
sudo -u postgres psql <<EOF
CREATE USER Omnibot WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE omnibot_db OWNER Omnibot;
GRANT ALL PRIVILEGES ON DATABASE omnibot_db TO Omnibot;
\q
EOF

echo "${GREEN}✓ Database created${NC}"

# Setup Redis
echo "${YELLOW}Step 4: Setting up Redis...${NC}"
sudo systemctl enable redis-server
sudo systemctl start redis-server
echo "${GREEN}✓ Redis started${NC}"

# Create directory structure
echo "${YELLOW}Step 5: Creating directory structure...${NC}"
mkdir -p ~/omnibot/{src/{config,data,database,ml,risk,trading,utils,gui,tests},logs,data,secrets,models,backups}
cd ~/omnibot
echo "${GREEN}✓ Directories created${NC}"

# Create virtual environment
echo "${YELLOW}Step 6: Creating Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
echo "${GREEN}✓ Virtual environment created${NC}"

# Install PyTorch (CPU version for Raspberry Pi)
echo "${YELLOW}Step 7: Installing PyTorch (CPU)...${NC}"
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
echo "${GREEN}✓ PyTorch installed${NC}"

# Copy source files
echo "${YELLOW}Step 8: Copying source files...${NC}"
# Note: Copy files from git clone directory to ~/omnibot
cp -r src/* ~/omnibot/src/
echo "${GREEN}✓ Source files copied${NC}"

# Install Python dependencies
echo "${YELLOW}Step 9: Installing Python dependencies...${NC}"
pip install -r requirements.txt
echo "${GREEN}✓ Dependencies installed${NC}"

# Download NLTK data
echo "${YELLOW}Step 10: Downloading NLTK data...${NC}"
python -m nltk.downloader punkt vader_lexicon stopwords wordnet
echo "${GREEN}✓ NLTK data downloaded${NC}"

# Create .env file
echo "${YELLOW}Step 11: Creating configuration file...${NC}"
cat > ~/omnibot/.env <<EOF
# OmniBot v2.5 Configuration
# Generated: $(date -Iseconds)

# API Keys (fill these in!)
ALPACA_API_KEY_ENC=''
ALPACA_SECRET_KEY_ENC=''
NEWSAPI_KEY_ENC=''
POLYGON_KEY_ENC=''

# Database
DATABASE_URL='postgresql://Omnibot:$DB_PASSWORD@localhost:5432/omnibot_db'
REDIS_URL='redis://localhost:6379/0'

# Trading Mode (paper/live/backtest)
TRADING_MODE='paper'

# Paths
MODEL_PATH='/home/Omnibot/omnibot/models'
DATA_PATH='/home/Omnibot/omnibot/data'
EOF

chmod 600 ~/omnibot/.env
echo "${GREEN}✓ Configuration file created${NC}"

# Install systemd service
echo "${YELLOW}Step 12: Installing systemd service...${NC}"
sudo cp omnibot-v2.5.service /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/omnibot-v2.5.service
sudo systemctl daemon-reload
sudo systemctl enable omnibot-v2.5.service
echo "${GREEN}✓ Service installed${NC}"

echo ""
echo "=================================="
echo "${GREEN}Setup Complete!${NC}"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Get your Alpaca API keys from https://alpaca.markets"
echo "2. Edit ~/omnibot/.env and add your API keys"
echo "3. Run: python src/main.py --setup"
echo "4. Start the bot: sudo systemctl start omnibot-v2.5.service"
echo ""
echo "Database password (save this!): $DB_PASSWORD"
echo ""
