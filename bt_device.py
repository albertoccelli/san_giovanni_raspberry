#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Automatically checks for new usb drives to perform the update of the SM Demo Software

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
import time

from utils import get_sinks, print_datetime, curwd


class Device:

    def __init__(self, name):
        self.name = name
        self.mac_address = None
        self.trusted = False
        self.paired = False
        self.connected = False
        self.sink = None
        self.ready_to_play = False
        self.get_mac_address()
        self.get_info()
        if not self.trusted:
            self.trust()
        if not self.paired:
            self.pair()
        if not self.connected:
            self.connect()
        else:
            print_datetime("Device already connected")

    def get_mac_address(self):
        ntry = 1
        maxtry = 10
        timeout = 10
        # check if the device is among device list of bluetoothctl
        get_devices = subprocess.run(["bluetoothctl", "devices"], capture_output=True, text=True)
        device_list = get_devices.stdout.split("\n")
        device_list.remove("")
        for i in range(len(device_list)):
            if self.name in device_list[i]:
                self.mac_address = device_list[i].split(" ")[1]
                self.name = " ".join(device_list[i].split(" ")[2:])
        # if the macaddres has not been found, then there's the need for a scan
        if self.mac_address is not None:
            return self.mac_address
        print_datetime("Please turn on the bluetooth device and put it in advertising mode")
        audio_prompt("prompts/turnon.wav")
        while ntry <= maxtry:
            bt_scan = subprocess.Popen(["bluetoothctl", "--timeout", str(timeout), "scan", "on"],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            bt_scan.wait()
            stdout, stderr = bt_scan.communicate()
            if stderr:
                pass
            else:
                output = subprocess.Popen(["bluetoothctl", "devices"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                          text=True)
                output.wait()
                stdout, stderr = output.communicate()
                device_list = stdout.split("\n")
                for i in range(len(device_list)):
                    if self.name in device_list[i]:
                        print_datetime(f"Found: {device_list[i]}")
                        audio_prompt("prompts/found.wav")
                        self.mac_address = device_list[i].split(" ")[1]
                        self.name = " ".join(device_list[i].split(" ")[2:])
                        break
                print_datetime("Device not found. Trying again...")
            if self.mac_address is not None:
                return self.mac_address
        print_datetime("Couldn't find the device. Please turn it on, place into pairing mode and try again")
        return

    def get_info(self):
        if self.mac_address:
            info_output = subprocess.run(["bluetoothctl", "info", self.mac_address], capture_output=True, text=True)
            info = info_output.stdout.split("\n")
            for i in info:
                if "Paired" in i:
                    if "yes" in i.lower():
                        self.paired = True
                    else:
                        self.paired = False
                if "Trusted" in i:
                    if "yes" in i.lower():
                        self.trusted = True
                    else:
                        self.trusted = False
                if "Connected" in i:
                    if "yes" in i.lower():
                        self.connected = True
                    else:
                        self.connected = False

    def connect(self):
        attempts = 0
        if self.mac_address:
            while True:
                print("Trying to connect...")
                connect = subprocess.run(["bluetoothctl", "connect", self.mac_address], capture_output=True, text=True)
                outcome = connect.stdout
                print_datetime(outcome)
                if "failed" in outcome.lower():
                    if attempts <= 5:
                        print_datetime("Failed to connect: please check that the device is turned on, then try again")
                        audio_prompt("prompts/error1.wav")
                    else:
                        print_datetime("Failed to connect. Please try putting the device into pairing mode")
                elif "success" in outcome.lower():
                    audio_prompt("prompts/connected.wav")
                    self.get_sink()
                    return
                attempts += 1

    def pair(self):
        attempts = 0
        if self.mac_address:
            print_datetime("Pairing...")
            pair = subprocess.run(["bluetoothctl", "pair", self.mac_address], capture_output=True, text=True)
            outcome = pair.stdout
            print_datetime(outcome)
            if "failed" in outcome.lower():
                if attempts <= 5:
                    print_datetime("Failed to pair: please check that the device is turned on, then try again")
                    audio_prompt("prompts/error1.wav")
                else:
                    print_datetime("Failed to pair. Please try putting the device into pairing mode")
            elif "success" in outcome.lower():
                audio_prompt("prompts/connected.wav")
                self.get_sink()
                return
            attempts += 1

    def trust(self):
        if self.mac_address:
            print_datetime("Trusting...")
            trust = subprocess.run(["bluetoothctl", "trust", self.mac_address], capture_output=True, text=True)
            outcome = trust.stdout
            print_datetime(outcome)

    def get_sink(self):
        sinks = get_sinks()
        try:
            self.sink = sinks[1]
            if len(sinks) == 2:
                self.ready_to_play = True
        except Exception as e:
            print(f"Error getting sinks: {e}")
            self.ready_to_play = False
            if not self.check_connected():
                self.connect()
            pass

    def check_connected(self):
        self.get_info()
        return self.connected


if __name__ == "__main__":
    from utils import audio_prompt, load_config

    config_file = f"{curwd}/config.yaml"
    config = load_config(config_file)
    device_name = config.get("device_name")


    def initialize(device):
        # after the connection, check if the device can listen to music
        while not device.ready_to_play:
            device.get_info()
            device.get_sink()
            time.sleep(1)
        print_datetime("Ready to play!")


    # initialize the neckband connection. Closes the program once it's ready to play
    neckband = Device(device_name)
    initialize(neckband)
