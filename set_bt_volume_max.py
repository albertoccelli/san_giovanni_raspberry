import subprocess
from get_sinks import getPaths
import time
import os
# get path of the bluetooth sink
try:
	command = "dbus-send --system --type=method_call --print-reply --dest='org.bluez' /org/bluez/hci0/dev_78_5E_A2_F9_A5_9A org.bluez.MediaControl1.VolumeUp"
	p = getPaths()[1]
	print(p)
	command = ["dbus-send", "--system", "--type=method_call", "--print-reply", "--dest=org.bluez" ,  "/org/bluez/hci0/dev_78_5E_A2_F9_A5_9A", "org.bluez.MediaControl1.VolumeUp"]
	for i in range(30):
		lowerVolume = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
		stdout, stderr = lowerVolume.communicate()
		lowerVolume.wait()
		print(stdout)
		time.sleep(0.05)



except Exception as e:
	print(e)
