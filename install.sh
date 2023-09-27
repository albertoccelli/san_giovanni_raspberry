#!/bin/bash

user_name=$USER
curwd=$PWD

# Install sm_demo script package
# Update package list and system
sudo apt-get update -y && sudo apt-get upgrade -y

# Add user
sudo adduser $USER bluetooth

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
sudo apt-get install python3-pip -y
pip install -r $PWD/requirements.txt
