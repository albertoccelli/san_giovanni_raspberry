### bt_device.py
### version: 0.1.2
### author: Alberto Occelli
###
### Usage: python bt_device.pu <Device name>
###
### Description: automatically connects bluetooth speaker.
###		Using bluetoothctl, looks for the device with the specified name.
###		Prompts audio messages to guide user along the pairing and connection process
###
###		If the device is not among the bluetooth.service device list, prompt message to turn on device and put
###		put in into advertisement mode. Then try connection
###		If the device is among the bluetooth.service list, try to connect. If it fails, prompt message to turn
###		on the device
###


import subprocess
import time
from get_sinks import getSinks
import os
from utils import audio_prompt

class Device:

	def __init__(self, name):
		self.name = name
		self.mac_address = None
		self.trusted = False
		self.paired = False
		self.connected = False
		self.sink = None
		self.ready_to_play = False

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
		audio_prompt("prompts/turnon.wav")
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
						audio_prompt("prompts/found.wav")
						self.mac_address = device_list[i].split(" ")[1]
						self.name = " ".join(device_list[i].split(" ")[2:])
						break
				print("Device not found. Trying again...")
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
		attempts = 0
		if self.mac_address:
			while True:
				print("Connecting...")
				connect = subprocess.run(["bluetoothctl", "connect", self.mac_address], capture_output = True, text = True)
				outcome = connect.stdout
				print(outcome)
				if "failed" in outcome.lower():
					if attempts <= 5:
						print("Failed to connect: please check that the device is turned on, then try again")
						audio_prompt("prompts/error1.wav")
					else:
						print("Failed to connect. Please try putting the device into pairing mode")
				elif "success" in outcome.lower():
					#audio_prompt("prompts/connected.wav")
					self.get_sink()
					return
				attempts+=1


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
			if len(sinks) == 2:
				self.ready_to_play = True
		except Exception as e:
			self.ready_to_play = False
			print("Device not ready to play yet")

	def check_connected(self):
		self.get_info()
		return self.connected

if __name__ == "__main__":
	from utils import start_player, stop_player
	import sys
	from utils import audio_prompt, load_config
	import yaml

	config_file = "/home/a.occelli/sm_demo/config.yaml"
	config = load_config(config_file)
	device_name = config.get("device_name")


	# first time try the connection
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


	# after the connection, check if the device can listen to music
	while neckband.ready_to_play == False:
		neckband.get_sink()
		time.sleep(1)

	print("Ready to play!")
	audio_prompt("/home/a.occelli/sm_demo/prompts/connected.wav")
