# SAN GIOVANNI PROJECT
Automaticaly connect to specified bluetooth device and start play music

## Installing
### What's needed
1. Raspberry Pi (model used for testing: Raspberry Pi 3A+)
2. PC 
3. Sensors:
   - Rotary encoder
   - Distance sensor (HC-SR04)
4. Power amplifier
5. Speaker
6. Bluetooth device (for testing a SONY Neckband was used)

### Manual install steps
#### Prepare the Raspberry Pi
1. Install the [Rasberry PI OS Lite](https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2023-05-03/2023-05-03-raspios-bullseye-armhf-lite.img.xz) version (the developing was performed over the version 11-Bullseye).
Make sure, during the install, to enable the ssh, in order to communicate with the raspberry via wireless network.
2. Once installed, connect via ssh
3. Enable the auto-console login via Raspi-config.
4. Update and upgrade:
   ```
   sudo apt-get update && sudo apt-get upgrade -y
   ```
5. Install GIT, Pulseaudio and Pip3:
   ```
   sudo apt-get install git pulseaudio python3-pip -y
   ```
6. The bluetooth A2DP won't work out-of-the-box: a few commands and editings are required:
   - Add the current user to the bluetooth group:
   ```
   sudo adduser $(whoami) bluetooth
   ```
   - Edit the bluetooth service file:
   ```
   sudo -E systemctl edit --full bluetooth
   ```
   - In the bluetooth service file, change the line
     ```
     ExecStart=/usr/libexec/bluetooth/bluetoothd
     ```
     to
     ```
     ExecStart=/usr/libexec/bluetooth/bluetoothd --noplugin=sap
     ```
   - Reload the daemon and restart the bluetooth service:
   ```
   sudo systemctl daemon-reload && sudo systemctl restart bluetooth
   ```
   - Install the Pulseaudio bluetooth module:
   ```
   sudo apt install --no-install-recommends pulseaudio-module-bluetooth -y
   ```
   - Finally, enable and start the pulseaudio service. This way, it will be loaded each time the Raspberry is booted:
   ```
   systemctl --user enable pulseaudio && systemctl --user start pulseaudio
   ```
#### Install the program suite

1. Download the program from git and move to the install folder:
   ```
   git clone https://github.com/albertoccelli/san_giovanni_raspberry && cd san_giovanni_raspberry
   ```
2. Add the current directory to the environment variables:
   ```
   echo "export SM_DIR=$(pwd)" >> ~/.bashrc && source ~/.bashrc
   ```
3. Install the pip requirements for the program:
   ```
   pip install -r requirements.txt
   ```
4. Launch the python script to install the needed service files:
   ```
   python service_install.py
   ```
