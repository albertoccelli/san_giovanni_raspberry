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

import time
import subprocess
import os

import pyudev

from utils import get_sinks, curwd


controlfile = ".update_smdemo.txt"
jack_sink = get_sinks()[0]
m_path = "/media/usb-drive"
t_path = curwd


def stop_player():
    # stop player.service
    stop_pl = subprocess.Popen(["systemctl", "--user", "stop", "player.service"])
    stop_pl.wait()
    return


def audio_prompt(filename):
    # play prompt
    play_prompt = subprocess.Popen(["paplay", f"--device={jack_sink}", filename])
    play_prompt.wait()


def start_player():
    # restart player.service
    restart_player = subprocess.Popen(["systemctl", "--user", "start", "player.service"])
    restart_player.wait()


def start_bt():
    # start bt_scan.service
    start_ble = subprocess.Popen(["systemctl", "--user", "start", "bt_scan.service"])
    start_ble.wait()


def stop_bt():
    stop_ble = subprocess.Popen(["systemctl", "--user", "stop", "bt_scan.service"])
    stop_ble.wait()


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
    create_mp = subprocess.Popen(["sudo", "mkdir", mount_path])
    create_mp.wait()
    # mount usb drive
    mount = subprocess.Popen(["sudo", "mount", usb_path, mount_path])
    mount.wait()
    print("Successfully mounted")


def usb_in_callback(event):
    if event.device_node is not None and event.action == "add":
        print(f"USB detected:")
        # get path of the usb
        path = wait_for_usb()
        print(path)
        s_path = path
        # mount the usb into the s_path folder
        mount_usb(s_path, m_path)
        update(m_path, t_path)
        return


def update(source, target):
    stop_player()
    stop_bt()
    # check if there is the source folder
    check = subprocess.Popen(["ls", "-a", f"{source}/sm_copy"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True)
    stdout, stderr = check.communicate()
    if stderr:
        # Case of error
        print("ERROR:")
        print(stderr)
        audio_prompt(f"{curwd}/prompts/usb_error.wav")
        start_player()
        return
    check = stdout.split("\n")
    print(check)
    time.sleep(0.5)
    # check if usb drive is allowed to update
    if controlfile in check:
        audio_prompt(f"{curwd}/prompts/wait_update.wav")
        # copy config file
        print("Copying configuration files")
        copy_config = f"cp -r {source}/sm_copy/*.yaml {target}"
        os.system(copy_config)
        # copy audio files for the neckband
        print("Copying neck audio file")
        neck_files = subprocess.check_output(["ls", f"{source}/sm_copy/"])
        print(neck_files)
        command = f"rsync -av --delete {source}/sm_copy/media/neck {target}/media/"
        os.system(command)
        # run script runme.sh inside the folder
        print("Running bash script")
        os.system(f"{source}/sm_copy/runme.sh")
        print("Done")
        # end update
        print("Copy successful")
        audio_prompt(f"{curwd}/prompts/update_complete.wav")
        start_player()
    else:
        audio_prompt(f"{curwd}/prompts/usb_error.wav")
        print("Not allowed to copy from this usb")
    time.sleep(1)
    start_player()
    start_bt()
    return


if __name__ == "__main__":

    # verify if there's a connected usb drive at boot
    drive = get_usb_path()
    if drive:
        print("Drive detected")
        mount_usb(drive, m_path)
        update(m_path, t_path)

    start_bt()
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
