# bt_device.py
# version: 0.1.2
# author: Alberto Occelli

import subprocess
import time
from get_sinks import getSinks
import os


class Device:

	def __init__(self, name):
		self.name = name
		self.mac_address = None
		self.trusted = False
		self.paired = False
		self.connected = False
		self.sing = None

	def get_mac_address(self):
		ntry = 1
		maxtry = 10
		timeout = 10
		#check if the device is among device list of bluetoothctl
		get_devices = subprocess.run(["bluetoothctl", "devices"], capture_output = True, text = True)
		device_list = get_devices.stdout.split("\n")
		device_list.remove("")
		for i in range(len(device_list)):
			if self.name in device_list[i]:
				print("Found!")
				self.mac_address = device_list[i].split(" ")[1]
				self.name = " ".join(device_list[i].split(" ")[2:])
		#if the macaddres has not been found, then there's the need for a scan
		if self.mac_address != None: return self.mac_address
		print("Please turn on the bluetooth device and put it in advertising mode")
		while ntry <= maxtry:
			bt_scan = subprocess.Popen(["bluetoothctl", "--timeout", str(timeout), "scan", "on"], stdout = subprocess.PIPE, stderr = subprocess.PIPE,text = True)
			bt_scan.wait()
			stdout, stderr = bt_scan.communicate()
			if stderr:
				pass
			else:
				output = subprocess.Popen(["bluetoothctl", "devices"], stdout = subprocess.PIPE, stderr = subprocess.PIPE,text = True)
				output.wait()
				stdout, stderr = output.communicate()
				device_list = stdout.split("\n")
				for i in range(len(device_list)):
					if self.name in device_list[i]:
						print(f"Found: {device_list[i]}")
						self.mac_address = device_list[i].split(" ")[1]
						self.name = " ".join(device_list[i].split(" ")[2:])
						break
			if self.mac_address != None: return self.mac_address
		print("Couldn't find the device. Please turn it on, place into pairing mode and try again")
		return


	def get_info(self):
		if self.mac_address:
			info_output = subprocess.run(["bluetoothctl", "info", self.mac_address], capture_output = True, text = True)
			info = info_output.stdout.split("\n")
			for i in info:
				if "Paired" in i:
					if "yes" in i.lower(): self.paired = True
				if "Trusted" in i:
					if "yes" in i.lower(): self.trusted = True
				if "Connected" in i:
					if "yes" in i.lower(): self.connected = True

	def connect(self):
		if self.mac_address:
			while True:
				print("Connecting...")
				connect = subprocess.run(["bluetoothctl", "connect", self.mac_address], capture_output = True, text = True)
				outcome = connect.stdout
				print(outcome)
				if "failed" in outcome.lower():
					print("Failed to connect: please check that the device is turned on, then try again")
				elif "success" in outcome.lower():
					self.get_sink()
					break

	def pair(self):
		if self.mac_address:
			print("Pairing...")
			pair = subprocess.run(["bluetoothctl", "pair", self.mac_address], capture_output = True, text = True)
			outcome = pair.stdout
			print(outcome)

	def trust(self):
		if self.mac_address:
			print("Trusting...")
			trust = subprocess.run(["bluetoothctl", "trust", self.mac_address], capture_output = True, text = True)
			outcome = trust.stdout
			print(outcome)

	def get_sink(self):
		sinks = getSinks()
		try:
			self.sink = sinks[1]
		except Exception as e:
			print(e)

	def check_connected(self):
		self.get_info()
		return self.connected

if __name__ == "__main__":
	import sys

	if len(sys.argv) < 2:
		print("Usage: python bt_device.py <device nane>")
		sys.exit(1)
	device_name = sys.argv[1]

	neckband = Device(device_name)
	neckband.get_mac_address()
	neckband.get_info()
	if not neckband.trusted: neckband.trust()
	if not neckband.paired: neckband.pair
	if not neckband.connected:
		neckband.connect()
	else:
		if Device.check_connected:
			print("Device already connected")

