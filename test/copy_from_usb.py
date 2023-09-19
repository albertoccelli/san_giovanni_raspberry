import pyudev
import os
import shutil
import subprocess
import time

def mount_usb(device):
	time.sleep(1)
	output = subprocess.check_output(["lsblk", "-fp"], shell = True, text = True)
	print(output.split("\n")[1:])
	mount_point = f"/media/usb"


def is_mounted(mount_point):
    try:
        subprocess.check_output(["sudo", "mountpoint", "-q", mount_point])
        return True
    except subprocess.CalledProcessError:
        return False


def copy_directory_to_usb(device):
	destination_directory = "."

context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by(subsystem="usb")
for device in iter(monitor.poll, None):
	if device.action == "add":
		try:
			mount_usb(device)
		except:
			pass
