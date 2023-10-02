# MESTRE PROJECT
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

### Install from sh script (Beta)
1. Make sure that git is installed
   ```
   sudo apt-get update && sudo apt-get upgrade
   sudo apt-get install git
   ```
2. Download the source folder: this can be done in two ways:
   - Clone the repository from github: 
   ```
   git clone https://github.com/albertoccelli/sm_demo
   ```
   - Download the .zip file of the lastest release version and unzip it: 
   ```
   wget https://github.com/albertoccelli/sm_demo/archive/master.zip
   unzip sm_demoX.X.zip sm_demo
   ```
3. Move into the SM Demo folder and install the program with the command:
   ```
   source install.sh
   ```
### Manual install steps
#### Prepare the Raspberry Pi
1. Install the [Rasberry PI OS Lite](https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2023-05-03/2023-05-03-raspios-bullseye-armhf-lite.img.xz) version (the developing was performed over the version 11-Bullseye).
Make sure, during the install, to enable the ssh, in order to communicate with the raspberry via wireless network.
2. Once installed, connect via ssh
3. Update and upgrade:
   ```
   sudo apt-get update && sudo apt-get upgrade
   ```
4. The bluetooth A2DP won't work out-of-the-box: a few commands and editings are required:
   - Add the user to the bluetooth group:
   ```
   sudo adduser pi bluetooth
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
   sudo systemctl daemon-reload
   sudo systemctl restart bluetooth
   ```
   - Install the Pulseaudio bluetooth module:
   ```
   sudo apt install --no-install-recommends pulseaudio-module-bluetooth
   ```
   - Finally, enable and start the pulseaudio service. This way, it will be loaded each time the Raspberry is booted:
   ```
   systemctl --user enable pulseaudio
   systemctl --user start pulseaudio
   ```
5. Install PIP, in order to install the python dependencies: 
   ```
   sudo apt-get install python3-pip
   ```
