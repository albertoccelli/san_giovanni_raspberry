#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
The Main loop routine of the SM Demo software. First starts by looking for a BT device, then starts
the SM Demo. When the SM demo ends due to disconnection, it once again try to connect to the BT

Requirements: Raspberry Pi 3
"""

__author__ = "Alberto Occelli"
__copyright__ = "Copyright 2023,"
__credits__ = ["Alberto Occelli"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Alberto Occelli"
__email__ = "albertoccelli@gmail.com"
__status__ = "Dev"

import subprocess

from utils import curwd

print(curwd)

while True:
    try:
        #  connect bluetooth device
        bt_connect = subprocess.Popen(["python", f"{curwd}/bt_device.py"])
        bt_connect.wait()
        #  start player service
        demo = subprocess.Popen(["python", f"{curwd}/sm_demo.py"])
        demo.wait()
    except KeyboardInterrupt:
        subprocess.Popen(["killall", "paplay"])
        break
