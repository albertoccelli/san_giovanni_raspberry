#!/bin/bash

user_name=$USER

# Install sm_demo script package
# Update package list
sudo apt-get update

# Upgrade the system
sudo apt-get upgrade

# Add user
sudo adduser $USER bluetooth

# Reload systemd daemon
sudo systemctl daemon-reload

# Restart bluetooth service
sudo systemctl restart bluetooth

# Install PulseAudion for Bluetooth
sudo apt install --no-install-recommends pulseaudio-module-bluetooth

# Enable PulseAudio for current user
systemctl --user enable pulseaudio
systemctl --user start pulseaudio
