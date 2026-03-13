#!/bin/bash
# OMNIBOT v2.5 - Raspberry Pi Setup Script (RUN AFTER SD CARD IS READY)
# This script assumes Raspberry Pi OS is already installed and you can SSH in

set -e

echo "=========================================="
echo "OMNIBOT v2.5 - Raspberry Pi Setup"
echo "Running on: $(hostname)"
echo "=========================================="
echo ""

# Check if running on Raspberry Pi
if [[ $(uname -m) != "aarch64" && $(uname -m) != "armv7l" ]]; then
    echo "⚠ Warning: This doesn't appear to be a Raspberry Pi"
    echo "Continuing anyway..."
    echo ""
fi

# Update system
echo "→ Updating system packages..."
sudo apt update && sudo apt full-upgrade -y

# Install system dependencies
echo "→ Installing system dependencies..."
sudo apt install -y python3-venv python3-pip python3-dev build-essential \
    libopenblas-dev liblapack-dev gfortran postgresql libpq-dev \
    redis-server git vim htop tree tmux sqlite3 libsqlite3-dev \
    pkg-config cmake libhdf5-dev

# Setup PostgreSQL (optional)
echo "→ Setting up PostgreSQL..."
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Generate database password
DB_PASS=$(openssl rand -base64 32)
echo ""
echo "=========================================="
echo "DATABASE PASSWORD (SAVE THIS):"
echo "$DB_PASS"
echo "=========================================="
echo ""

# Create database user and database
sudo -u postgres psql -c "CREATE USER omnibot WITH PASSWORD '$DB_PASS';" 2>/dev/null || echo "User may already exist"
sudo -u postgres psql -c "CREATE DATABASE omnibot_db OWNER omnibot;" 2>/dev/null || echo "Database may already exist"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE omnibot_db TO omnibot;"

# Setup Redis
echo "→ Setting up Redis..."
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Create project directory
echo "→ Creating project directory..."
PROJECT_DIR="$HOME/omnibot-v2.5"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Create virtual environment
echo "→ Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "→ Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install PyTorch (CPU version for Pi)
echo "→ Installing PyTorch (this takes 10-15 minutes)..."
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install requirements
echo "→ Installing Python packages (this takes 15-30 minutes)..."
pip install -r requirements.txt

# Download NLTK data
echo "→ Downloading NLTK data..."
python -m nltk.downloader punkt vader_lexicon stopwords wordnet

# Create directory structure
echo "→ Creating directories..."
mkdir -p models data logs backups secrets

# Create .env file
echo "→ Creating initial .env file..."
cat > .env << EOF
# OMNIBOT v2.5 Configuration
# Generated: $(date -Iseconds)

ALPACA_API_KEY_ENC=''
ALPACA_SECRET_KEY_ENC=''
NEWSAPI_KEY_ENC=''
POLYGON_KEY_ENC=''

DATABASE_URL='postgresql://omnibot:$DB_PASS@localhost:5432/omnibot_db'
REDIS_URL='redis://localhost:6379/0'
TRADING_MODE='paper'

MODEL_PATH='./models'
DATA_PATH='./data'
EOF

chmod 600 .env

echo ""
echo "=========================================="
echo "✓ SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Configure API keys:"
echo "   python src/main.py --setup"
echo ""
echo "2. Test installation:"
echo "   python src/main.py --trades"
echo ""
echo "3. Start paper trading:"
echo "   python src/main.py --mode cli"
echo ""
echo "4. Install as service (optional):"
echo "   sudo ./scripts/install-service.sh"
echo ""
echo "Database password saved in: $PROJECT_DIR/.env"
echo ""
