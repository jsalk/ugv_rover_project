#!/bin/bash
# install_dependencies.sh
# UGV Rover dependency installation script

echo "Installing UGV Rover dependencies..."
echo "This script requires sudo privileges."

# Update package list
sudo apt update

# Install system dependencies
sudo apt install -y python3-pip python3-pygame bluetooth bluez

# Install Python packages
sudo pip3 install -r requirements.txt

# Enable Bluetooth service
sudo systemctl enable bluetooth
sudo systemctl start bluetooth

echo "Dependencies installed successfully!"
echo ""
echo "Next steps:"
echo "1. Pair your Xbox controller:"
echo "   bluetoothctl"
echo "   [bluetooth]# scan on"
echo "   [bluetooth]# pair [MAC_ADDRESS]"
echo "   [bluetooth]# trust [MAC_ADDRESS]"
echo ""
echo "2. Test motors: python3 test_motors.py"
echo "3. Calibrate directions: python3 calibrate_motors.py"
echo "4. Start controller: python3 ugv_xbox_controller.py"