#!/bin/bash

TO_INSTALL=$1
INSTALL_LOCATION=~/.config/systemd/user/

echo "Installing service $TO_INSTALL into location $INSTALL_LOCATION"
# copy service into user install location
echo "Copying files into install location"
cp $TO_INSTALL $INSTALL_LOCATION
echo "Enabling service"
systemctl --user enable $TO_INSTALL

echo "Install complete!"
read -p "Do you want to reboot the system now? (y/n)" answer
if [ $answer == "y" ] ; then
	echo "Rebooting..."
	sudo reboot now
elif [ $answer == "n" ] ; then
	echo "Starting service $TO_INSTALL"
	systemctl --user daemon-reload
	systemctl --user start $TO_INSTALL
fi
