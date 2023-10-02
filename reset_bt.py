#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Removes any BT binding

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

devices = subprocess.Popen(["bluetoothctl", "devices"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
devices.wait()
stdout, stderr = devices.communicate()

devices = stdout.decode("utf-8").split("\n")

mac_addresses = []
for i in range(len(devices)):
	try:
		mac_addresses.append(devices[i].split(" ")[1])
	except Exception as e:
		print(e)
		pass
print(mac_addresses)

for m in mac_addresses:
	command = ["bluetoothctl", "disconnect", m]
	rm_devices = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	rm_devices.wait()
	command = ["bluetoothctl", "remove", m]
	rm_devices = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	rm_devices.wait()

print("Done!")
