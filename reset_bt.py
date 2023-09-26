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
