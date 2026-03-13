#!/bin/bash
# OMNIBOT v2.5 - Protected Setup Script
# Copyright (c) 2026 3D-Magic
# LICENSE: Personal Use Only

set -e

echo "=========================================="
echo "OMNIBOT v2.5 - Protected Setup"
echo "=========================================="
echo ""

# Check if running on Raspberry Pi
if [[ $(uname -m) != "aarch64" && $(uname -m) != "armv7l" ]]; then
    echo "⚠ Warning: This doesn't appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "📜 LICENSE: Personal Use Only"
echo "   - Free for personal trading"
echo "   - NO modifications permitted"
echo "   - NO redistribution allowed"
echo ""
read -p "Do you agree to these terms? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup aborted."
    exit 1
fi

echo ""
echo "→ Updating system packages..."
sudo apt update && sudo apt full-upgrade -y

echo "→ Installing system dependencies..."
sudo apt install -y python3-venv python3-pip python3-dev build-essential \
    libopenblas-dev liblapack-dev gfortran postgresql libpq-dev \
    redis-server git vim htop tree tmux sqlite3 libsqlite3-dev \
    pkg-config cmake libhdf5-dev openssl

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

sudo -u postgres psql -c "CREATE USER omnibot WITH PASSWORD '$DB_PASS';" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE omnibot_db OWNER omnibot;" 2>/dev/null || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE omnibot_db TO omnibot;"

echo "→ Setting up Redis..."
sudo systemctl enable redis-server
sudo systemctl start redis-server

echo "→ Creating Python environment..."
python3 -m venv venv
source venv/bin/activate

echo "→ Installing Python packages..."
pip install --upgrade pip setuptools wheel

echo "→ Installing PyTorch (this takes 10-15 minutes)..."
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

echo "→ Installing dependencies..."
pip install -r requirements.txt

echo "→ Downloading NLP data..."
python -m nltk.downloader punkt vader_lexicon stopwords wordnet

echo "→ Creating directories..."
mkdir -p models data logs backups secrets

echo "→ Generating security hashes..."
python -c "
import sys
sys.path.insert(0, 'src')
from security.protector import LicenseProtector
p = LicenseProtector()
p._generate_hashes()
print('✓ Integrity hashes generated')
"

echo ""
echo "=========================================="
echo "✓ SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "⚠️  IMPORTANT SECURITY NOTES:"
echo ""
echo "1. Change the admin password in:"
echo "   src/security/protector.py"
echo "   (Edit ADMIN_PASSWORD_HASH line)"
echo ""
echo "2. To configure API keys, run:"
echo "   python src/main.py --setup"
echo "   (Requires admin password)"
echo ""
echo "3. The bot will NOT start if files are modified"
echo ""
echo "4. Database password saved in: .env"
echo ""
echo "=========================================="
