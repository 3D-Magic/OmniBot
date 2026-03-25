#!/bin/bash
# OMNIBOT v2.6 Sentinel - Clean Install Script
# Wipes old versions and installs fresh

set -e

REPO_URL="https://github.com/3D-Magic/OmniBot-Testing"
INSTALL_DIR="$HOME/OmniBot-v2.6"
BACKUP_DIR="$HOME/.omnibot-backups"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║   🤖  OMNIBOT v2.6 Sentinel - Clean Installer            ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] $1${NC}"
}

# Backup existing installation
backup_existing() {
    if [ -d "$INSTALL_DIR" ]; then
        log "Backing up existing installation..."
        mkdir -p "$BACKUP_DIR"
        BACKUP_NAME="backup-$(date +%Y%m%d-%H%M%S).tar.gz"
        tar -czf "$BACKUP_DIR/$BACKUP_NAME" -C "$HOME" "$(basename "$INSTALL_DIR")" 2>/dev/null || true
        log "Backup saved to: $BACKUP_DIR/$BACKUP_NAME"
    fi
}

# Kill running processes
cleanup_processes() {
    log "Cleaning up old processes..."
    pkill -9 -f "omnibot" 2>/dev/null || true
    pkill -9 -f ngrok 2>/dev/null || true
    tmux kill-server 2>/dev/null || true
    sleep 2
}

# Remove old installation
remove_old() {
    if [ -d "$INSTALL_DIR" ]; then
        warn "Removing old installation at $INSTALL_DIR..."
        rm -rf "$INSTALL_DIR"
    fi

    # Clean up any stray files
    rm -f "$HOME/omnibot-v2.6*.zip" 2>/dev/null || true
}

# Download and install
install_new() {
    log "Downloading OMNIBOT v2.6 Sentinel..."
    cd "$HOME"

    # Download from main branch
    wget -q --show-progress "$REPO_URL/archive/refs/heads/main.zip" -O omnibot-v2.6.zip || {
        error "Failed to download from GitHub"
        exit 1
    }

    log "Extracting..."
    unzip -q omnibot-v2.6.zip
    mv OmniBot-Testing-main OmniBot-v2.6
    rm omnibot-v2.6.zip

    cd "$INSTALL_DIR"

    # Fix tensorflow issue (Python 3.13 compatibility)
    log "Applying Python 3.13 compatibility fixes..."
    sed -i '/tensorflow/d' requirements.txt 2>/dev/null || true
    sed -i '/keras/d' requirements.txt 2>/dev/null || true

    # Run setup
    log "Running setup..."
    chmod +x setup.sh
    ./setup.sh

    # Make scripts executable
    chmod +x scripts/omnibot.sh 2>/dev/null || true
    chmod +x clean-install.sh 2>/dev/null || true
}

# Create symlink for global access
create_symlink() {
    log "Creating global command..."
    mkdir -p "$HOME/.local/bin"
    ln -sf "$INSTALL_DIR/scripts/omnibot.sh" "$HOME/.local/bin/omnibot" 2>/dev/null || true

    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        warn "Add to your PATH: export PATH="\$HOME/.local/bin:\$PATH""
    fi
}

# Main
main() {
    log "Starting clean installation..."

    backup_existing
    cleanup_processes
    remove_old
    install_new
    create_symlink

    echo ""
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║                                                          ║"
    echo "║   ✅  Installation Complete!                             ║"
    echo "║                                                          ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    log "OMNIBOT v2.6 Sentinel is ready!"
    echo ""
    echo "Quick Start:"
    echo "  cd $INSTALL_DIR"
    echo "  ./scripts/omnibot.sh start --ngrok"
    echo ""
    echo "Or use global command (if PATH is set):"
    echo "  omnibot start --ngrok"
    echo ""
    echo "Access:"
    echo "  Local:    http://localhost:8081"
    echo "  External: https://xxxx.ngrok-free.dev (after starting with --ngrok)"
}

main "$@"
