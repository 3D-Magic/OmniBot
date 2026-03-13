#!/bin/bash
# Install OMNIBOT v2.5 as systemd service
# Run this AFTER setup.sh is complete

if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Get the user who ran sudo
if [ -z "$SUDO_USER" ]; then
    echo "Error: Could not determine user. Run with sudo."
    exit 1
fi

USERNAME=$SUDO_USER
INSTALL_DIR="/home/$USERNAME/omnibot-v2.5"

echo "Installing OMNIBOT v2.5 service..."
echo "User: $USERNAME"
echo "Directory: $INSTALL_DIR"

if [ ! -d "$INSTALL_DIR" ]; then
    echo "Error: Directory $INSTALL_DIR not found!"
    echo "Run setup.sh first."
    exit 1
fi

# Create systemd service file
cat > /etc/systemd/system/omnibot.service << EOF
[Unit]
Description=OMNIBOT v2.5 Trading System
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=$USERNAME
Group=$USERNAME
WorkingDirectory=$INSTALL_DIR
Environment="PYTHONPATH=$INSTALL_DIR/src"
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=$INSTALL_DIR/.env
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/src/main.py --mode cli
ExecStop=/bin/kill -SIGINT \$MAINPID
Restart=always
RestartSec=10
StartLimitInterval=60s
StartLimitBurst=3

[Install]
WantedBy=multi-user.target
EOF

# Reload and enable
systemctl daemon-reload
systemctl enable omnibot.service

echo ""
echo "✓ Service installed!"
echo ""
echo "Commands:"
echo "  Start:   sudo systemctl start omnibot"
echo "  Stop:    sudo systemctl stop omnibot"
echo "  Status:  sudo systemctl status omnibot"
echo "  Logs:    sudo journalctl -u omnibot -f"
echo ""
echo "To start now: sudo systemctl start omnibot"
