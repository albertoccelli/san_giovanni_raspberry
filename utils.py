#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Utility functions for SM Demo software

Changelog:
1.5.1 - bugfix
1.5.0 - added function to get bluez path
1.4.0 - added function to reload services
1.3.0 - added function to get mute status
1.2.0 - added function to get volume
1.1.0 - added functions to convert mp3 to wav
1.0.0 - file created

Requirements: Raspberry Pi 3
"""

__author__ = "Alberto Occelli"
__copyright__ = "Copyright 2023,"
__credits__ = ["Alberto Occelli"]
__license__ = "MIT"
__version__ = "1.5.1"
__maintainer__ = "Alberto Occelli"
__email__ = "albertoccelli@gmail.com"
__status__ = "Dev"

import subprocess
import yaml
import time
import os
from datetime import datetime

curwd = os.environ["SM_DIR"]
home = os.environ["HOME"]

def reload_system():
    service_dir = f"{curwd}/services"
    services = []
    files = os.listdir(service_dir)
    for f in files:
        if ".service" in f:
            services.append(f)
    print(services)
    for s in services:
        os.system(f"systemctl --user daemon-reload && systemctl --user restart {s}")


def convert_mp3_to_wav(source):
    if ".mp3" in source:
        wav_file = f"{source.split('.mp3')[0]}.wav"
        print(f"Converting {source} into {wav_file}")
        # os.system(f"mpg123 -q -w {wav_file} {source}")
        subprocess.run(["mpg123", "-q", "-w", wav_file, source])


def convert_media():
    media_dir = f"{curwd}/media"
    print(media_dir)
    # get all mp3 files into directory
    print("Mp3 files found:")
    mp3_files = []
    for root, _, files in os.walk(media_dir):
        for filename in files:
            if filename.endswith(".mp3"):
                mp3_file = os.path.join(root, filename)
                mp3_files.append(mp3_file)
                convert_mp3_to_wav(mp3_file)
                os.remove(mp3_file)


def print_datetime(argument):
    print(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\t{argument}")


def set_spkr_volume_max():
    try:
        bluez = get_bluez()
        command = ["dbus-send", "--system", "--type=method_call", "--print-reply", "--dest=org.bluez",
                   bluez, "org.bluez.MediaControl1.VolumeUp"]
        print_datetime("Setting neckband volume at maximum")
        for i in range(30):
            raise_volume = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            raise_volume.wait()
            # print(stdout)
            time.sleep(0.05)
        print_datetime("Done")
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

def save_parameter(file_path, parameter, new_value):
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)
    if parameter in data:
        data[parameter] = new_value
    else:
        print("Parameter not found")
    with open(file_path, 'w') as file:
        yaml.dump(data, file, default_flow_style=False)

def stop_player():
    # stop player.service
    s_player = subprocess.Popen(["systemctl", "--user", "stop", "player.service"])
    s_player.wait()


def audio_prompt(filename, sink=None):
    # play prompt
    if sink is None:
        sink = jack_sink
    subprocess.Popen(["pactl", "suspend-sink", "0"])
    play_prompt = subprocess.Popen(["paplay", f"--device={sink}", filename])
    play_prompt.wait()


def start_player():
    # restart player.service
    subprocess.Popen(["pactl", "suspend-sink", "0"])
    restart_player = subprocess.Popen(["systemctl", "--user", "start", "player.service"])
    restart_player.wait()


def get_bluez(sink=None):
    if sink is None:
        sink = get_sinks()[1]
    bluez = ""
    cur_sink = ""
    command = "pactl list sinks"
    output = subprocess.check_output(command, shell=True, text=True)
    output_lines = output.splitlines()

    volumes = {}
    for line in output_lines:
        if "Name" in line:
            cur_sink = line.split(":")[-1].replace(" ", "")
        if "bluez.path" in line:
            if cur_sink == sink:
                bluez = line.split("=")[-1].replace(" ", "").replace('"', '')
    return bluez


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
    for line in output_lines:
        if "Name" in line:
            names.append(line.split(":")[-1].replace(" ", ""))
    return names


def get_mute():
    command = "pactl list sinks"
    sink = ""

    output = subprocess.check_output(command, shell=True, text=True)
    output_lines = output.splitlines()

    muted = {}
    for line in output_lines:
        if "Name" in line:
            sink = line.split(":")[-1].replace(" ", "")
        if "Mute" in line:
            m = line.split("Mute: ")[-1]
            if m == "no":
                mute = False
            elif m == "yes":
                mute = True
            else:
                mute = None
            muted[sink] = mute
    return muted


def get_volumes(style="perc"):
    command = "pactl list sinks"
    sink = ""

    output = subprocess.check_output(command, shell=True, text=True)
    output_lines = output.splitlines()

    volumes = {}
    for line in output_lines:
        if "Name" in line:
            sink = line.split(":")[-1].replace(" ", "")
        if "Volume" in line:
            if "Base" not in line:
                vols = line.split("Volume:")[-1].split(",")
                stereo = []
                for i in range(len(vols)):
                    if style == "abs":
                        stereo.append(float(vols[i].split(":")[-1].split(" / ")[0].replace(" ", "")))
                    elif style == "perc":
                        stereo.append(float(vols[i].split(":")[-1].split(" / ")[1].replace(" ", "").replace("%", "")))
                    elif style == "db":
                        stereo.append(float(vols[i].split(":")[-1].split(" / ")[2].replace(" ", "").replace("dB", "")))
                value = sum(stereo) / len(stereo)
                volumes[sink] = value
    return volumes


def get_volume(sink, style="perc"):
    return get_volumes(style)[sink]


jack_sink = get_sinks()[0]
