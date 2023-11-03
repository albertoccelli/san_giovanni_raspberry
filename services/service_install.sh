#!/bin/bash

TO_INSTALL=$1
NAME=$(basename $TO_INSTALL)
INSTALL_LOCATION=~/.config/systemd/user/

echo "Installing service $NAME, located into $TO_INSTALL, into location $INSTALL_LOCATION"
# copy service into user install location
echo "Copying files into install location. Env variable: $SM_DIR"
sed 's#/path/to/#'$SM_DIR'/#g' $TO_INSTALL > $INSTALL_LOCATION/$NAME
echo "Enabling service"
systemctl --user enable $TO_INSTALL
systemctl --user daemon-reload
systemctl --user start $TO_INSTALL

echo "$TO_INSTALL service installation complete!"
