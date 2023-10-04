#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Utility functions for SM Demo software

Changelog:
1.1.0 - added functions to convert mp3 to wav
1.0.0 - file created

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
import yaml
import time
import os
from datetime import datetime

curwd = os.environ["SM_DIR"]


def convert_mp3_to_wav(source):
    if ".mp3" in source:
        wav_file = f"{source.split('.mp3')[0]}.wav"
        print(f"mpg123 -w {wav_file} {source}")
        # os.system(f"mpg123 -w {wav_file} {source}")


def convert_media():
    print(f"{curwd}/media")
    pass


def print_datetime(argument):
    print(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\t{argument}")


def set_spkr_volume_max():
    try:
        command = ["dbus-send", "--system", "--type=method_call", "--print-reply", "--dest=org.bluez",
                   "/org/bluez/hci0/dev_78_5E_A2_F9_A5_9A", "org.bluez.MediaControl1.VolumeUp"]
        for i in range(30):
            raise_volume = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            raise_volume.wait()
            # print(stdout)
            time.sleep(0.05)
    except Exception as e:
        print(e)


def load_config(file):
    with open(file, "r") as stream:
        try:
            configuration = yaml.safe_load(stream)
            return configuration
        except yaml.YAMLError as e:
            print(f"Error: {e}")
            return None


def stop_player():
    # stop player.service
    s_player = subprocess.Popen(["systemctl", "--user", "stop", "player.service"])
    s_player.wait()


def audio_prompt(filename):
    # play prompt
    subprocess.Popen(["pactl", "suspend-sink", "0"])
    play_prompt = subprocess.Popen(["paplay", f"--device={jack_sink}", filename])
    play_prompt.wait()


def start_player():
    # restart player.service
    subprocess.Popen(["pactl", "suspend-sink", "0"])
    restart_player = subprocess.Popen(["systemctl", "--user", "start", "player.service"])
    restart_player.wait()


def check_player():
    # check if player is running
    check = subprocess.Popen(["systemctl", "--user", "is-active", "player.service"], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, text=True)
    stdout, stderr = check.communicate()
    if "active" in stdout:
        if "inactive" in stdout:
            return False
        else:
            return True
    else:
        print("Error")


def get_sinks():
    command = "pactl list sinks"

    output = subprocess.check_output(command, shell=True, text=True)
    output_lines = output.splitlines()

    names = []
    paths = []
    for line in output_lines:
        if "Name" in line:
            names.append(line.split(":")[-1].replace(" ", ""))
        if "bluez.path" in line:
            paths.append(line.split(":")[-1].replace('"', '').replace(' ', ''))
    return names


def get_volumes(style="perc"):
    command = "pactl list sinks"

    output = subprocess.check_output(command, shell=True, text=True)
    output_lines = output.splitlines()

    volumes = []
    for line in output_lines:
        if "Volume" in line:
            if "Base" not in line:
                vols = line.split("Volume:")[-1].split(",")
                stereo = []
                for i in range(len(vols)):
                    if style == "abs":
                        stereo.append(vols[i].split(":")[-1].split(" / ")[0].replace(" ", ""))
                    elif style == "perc":
                        stereo.append(vols[i].split(":")[-1].split(" / ")[1].replace(" ", ""))
                    elif style == "db":
                        stereo.append(vols[i].split(":")[-1].split(" / ")[2].replace(" ", ""))
                volumes.append(stereo)
    return volumes


def get_paths():
    command = "pactl list sinks"

    output = subprocess.check_output(command, shell=True, text=True)
    output_lines = output.splitlines()

    names = []
    paths = []
    for line in output_lines:
        if "Name" in line:
            names.append(line.split(":")[-1].replace(" ", ""))
        if ".path" in line:
            paths.append(line.split("=")[-1].replace('"', '').replace(' ', ''))
    return paths


jack_sink = get_sinks()[0]
