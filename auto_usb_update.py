#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Automatically checks for new usb drives to perform the update of the SM Demo Software

Changelog:
- 1.3.0: update from zip
- 1.2.0: support for multilanguage
- 1.1.0: added functionality to automatically convert mp3 to wav when importing
- 1.0.0: file created

Requirements: Raspberry Pi 3
"""

__author__ = "Alberto Occelli"
__copyright__ = "Copyright 2023,"
__credits__ = ["Alberto Occelli"]
__license__ = "MIT"
__version__ = "1.3.0"
__maintainer__ = "Alberto Occelli"
__email__ = "albertoccelli@gmail.com"
__status__ = "Dev"

import time
import subprocess
import os

import pyudev

from utils import get_sinks, curwd, convert_media
from config import lang

controlfile = ".update_smdemo.txt"
jack_sink = get_sinks()[0]
m_path = "/media/usb-drive"
t_path = curwd


def stop_player():
    # stop player.service
    stop_pl = subprocess.Popen(["systemctl", "--user", "stop", "player.service"])
    stop_pl.wait()
    stop_pl = subprocess.Popen(["systemctl", "--user", "stop", "main_demo.service"])
    stop_pl.wait()
    return


def audio_prompt(filename):
    # play prompt
    play_prompt = subprocess.Popen(["paplay", f"--device={jack_sink}", filename])
    play_prompt.wait()


def start_player():
    # restart player.service
    restart_player = subprocess.Popen(["systemctl", "--user", "start", "main_demo.service"])
    restart_player.wait()


def get_usb_path():
    path = None
    disk = subprocess.check_output(["lsblk", "-p"]).decode("utf-8")
    disk = disk.split("\n")
    for d in disk:
        d = d.split(" ")
        while True:
            try:
                d.remove("")
            except ValueError:
                break
        if len(d) > 1 and d[2] == "1":  # check if removable
            if "part" in d[5]:  # check if it's a partition
                path = d[0].split("─")[-1]
    return path


def wait_for_usb():
    path = ""
    path_found = False
    while not path_found:
        disk = subprocess.check_output(["lsblk", "-p"]).decode("utf-8")
        disk = disk.split("\n")
        for d in disk:
            d = d.split(" ")
            while True:
                try:
                    d.remove("")
                except ValueError:
                    break
            if len(d) > 1 and d[2] == "1":  # check if removable
                if "part" in d[5]:  # check if it's a partition
                    path_found = True
                    path = d[0].split("─")[-1]
    return path


def mount_usb(usb_path, mount_path):
    print(f"Mounting usb on {mount_path}")
    # create mount point
    create_mp = subprocess.Popen(["sudo", "mkdir", mount_path], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout, stderr = create_mp.communicate()
    if stdout:
        print(f"Output: {stdout.decode('utf-8')}")
    if stderr:
        print("Mount folder already exists: skipping creation")
    # mount usb drive
    mount = subprocess.Popen(["sudo", "mount", usb_path, mount_path])
    mount.wait()
    print("Successfully mounted")


def usb_in_callback(event):
    if event.device_node is not None and event.action == "add":
        print(f"USB detected")
        # get path of the usb
        print("Getting USB path")
        path = wait_for_usb()
        print("Done")
        print(path)
        s_path = path
        # mount the usb into the s_path folder
        mount_usb(s_path, m_path)
        update(m_path, t_path)
        return


def update(source, target):
    print(f"Update in progress ({source} -> {target})")
    stop_player()
    # check if there is the source folder
    check = subprocess.Popen(["ls", "-a", f"{source}/sg_update"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True)
    stdout, stderr = check.communicate()
    if stderr:
        # Case of error
        print("ERROR:")
        print(stderr)
        print("USB drive not suitable for update")
        audio_prompt(f"{curwd}/prompts/{lang}/usb_error.wav")
        start_player()
        return
    print("SM UPDATE folder found!")
    check = stdout.split("\n")
    print(check)
    files = os.listdir(f"{source}/sg_update/")
    tar_files = []
    for f in files:
        if "tar.gz" in f:
            tar_files.append(f)
    update_file = tar_files[-1]
    print(f"Udpate file: {update_file}")
    time.sleep(0.1)
    # check if usb drive is allowed to update
    if True:
        audio_prompt(f"{curwd}/prompts/eng/wait_update.wav")
        # 1. copy tar file into home
        print("1/4 Copying configuration files")
        copy_config = f"cp -r {source}/sg_update/*.tar.gz {target}"
        print(copy_config)
        os.system(copy_config)
        # 2. extract files
        unzip = f"tar -xzvf {curwd}/{update_file} -C {curwd}/"
        print(unzip)
        os.system(unzip)
        #print("2/4 Copying audio files in media folder")
        #os.system(f"cp -r {source}/sm_copy/media {target}/")
        print("Done!")
        print("Update successful")
        audio_prompt(f"{curwd}/prompts/{lang}/update_complete.wav")
        start_player()
    else:
        audio_prompt(f"{curwd}/prompts/{lang}/usb_error.wav")
        print("Not allowed to copy from this usb")
    time.sleep(1)
    start_player()
    return


if __name__ == "__main__":

    # verify if there's a connected usb drive at boot
    drive = get_usb_path()
    if drive:
        print("Drive detected")
        mount_usb(drive, m_path)
        update(m_path, t_path)

    context = pyudev.Context()

    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='usb')

    observer = pyudev.MonitorObserver(monitor, callback=usb_in_callback)
    observer.start()

    try:
        observer.join()
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
