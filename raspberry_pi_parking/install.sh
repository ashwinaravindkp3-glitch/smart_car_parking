#!/bin/bash
#
# Raspberry Pi Smart Parking System - Installation Script
# Run this script on a fresh Raspberry Pi to install all dependencies
#

set -e  # Exit on error

echo "=========================================="
echo "Raspberry Pi Smart Parking System"
echo "Automated Installation Script"
echo "=========================================="
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "WARNING: This doesn't appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "ERROR: Please run this script as a normal user, not root"
    echo "Usage: bash install.sh"
    exit 1
fi

echo "Step 1/6: Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

echo ""
echo "Step 2/6: Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    python3-opencv \
    python3-rpi.gpio \
    libopencv-dev \
    libzbar0 \
    libzbar-dev \
    v4l-utils \
    git

echo ""
echo "Step 3/6: Installing Python packages..."
pip3 install -r requirements.txt

echo ""
echo "Step 4/6: Adding user to required groups..."
sudo usermod -a -G gpio $USER
sudo usermod -a -G video $USER

echo ""
echo "Step 5/6: Testing camera devices..."
if ls /dev/video* 1> /dev/null 2>&1; then
    echo "✓ Camera devices found:"
    ls -l /dev/video*
else
    echo "⚠ WARNING: No camera devices found"
    echo "  Please connect cameras and reboot"
fi

echo ""
echo "Step 6/6: Setting up systemd service..."
read -p "Do you want to install as a system service? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    CURRENT_DIR=$(pwd)
    SERVICE_FILE="/etc/systemd/system/parking.service"

    sudo bash -c "cat > $SERVICE_FILE" << EOF
[Unit]
Description=Raspberry Pi Smart Parking System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$CURRENT_DIR
ExecStart=/usr/bin/python3 $CURRENT_DIR/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable parking.service

    echo "✓ Service installed successfully"
    echo ""
    echo "Service commands:"
    echo "  Start:   sudo systemctl start parking.service"
    echo "  Stop:    sudo systemctl stop parking.service"
    echo "  Status:  sudo systemctl status parking.service"
    echo "  Logs:    sudo journalctl -u parking.service -f"
fi

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit config.py to configure:"
echo "   - Camera indices"
echo "   - GPIO pins"
echo "   - MQTT credentials (if needed)"
echo "   - Slot mapping"
echo ""
echo "2. Test the system:"
echo "   sudo python3 main.py"
echo ""
echo "3. IMPORTANT: Logout and login again for group changes to take effect"
echo "   Or reboot: sudo reboot"
echo ""
echo "For help, see README.md"
echo ""
