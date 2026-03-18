#!/bin/bash
# OMNIBOT v3.0 - Weekend Update Script
# Safe to run when market is closed

echo "=========================================="
echo "OMNIBOT v3.0 - Weekend Update"
echo "=========================================="
echo ""

# Check if market is open (simple check - US market hours)
hour=$(date +%H)
day=$(date +%u)  # 1=Monday, 7=Sunday

if [ "$day" -lt 6 ] && [ "$hour" -ge 13 ] && [ "$hour" -lt 21 ]; then
    echo "⚠️  WARNING: US market may be open!"
    read -p "Continue anyway? (y/N): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        echo "Update cancelled"
        exit 0
    fi
fi

echo "✓ Market is closed or weekend - safe to update"
echo ""

# Run standard update
bash update.sh

echo ""
echo "Weekend maintenance complete!"
echo "Bot will resume trading at next market open."
