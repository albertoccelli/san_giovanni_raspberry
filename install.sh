#!/bin/bash

user_name=$USER
curwd=$PWD

# Install sm_demo script package
# Update package list and system
echo "Upgrading the system..."
sudo apt-get update -y && sudo apt-get upgrade -y
echo "Done"

# Add user
sudo adduser $USER bluetooth

# Copy modified bluetooth service into systemd
echo "Copying modified bluetooth service into system..."
sudo cp $PWD/services/bluetooth.service /etc/systemd/system/
echo "Done!"

# Reload systemd daemon
sudo systemctl daemon-reload

# Restart bluetooth service
sudo systemctl restart bluetooth

# Install PulseAudion for Bluetooth
sudo apt install --no-install-recommends pulseaudio-module-bluetooth -y

# Enable PulseAudio for current user
systemctl --user enable pulseaudio
systemctl --user start pulseaudio

# Install dependencies for Python
echo "Installing Python dependencies..."
sudo apt-get install python3-pip -y
pip install -r $PWD/requirements.txt
echo "Done!"
