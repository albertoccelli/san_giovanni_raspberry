#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Player class for Raspberry Pi3. Can set up audio sink and play/pause/stop the reproducing of WAV files

Changelogs:
1.7.0 - BLACKBIRD - second stable release: added bluetooth unpairing function/enhanced performances
1.6.0 - ACROSS THE UNIVERSE - first stable release

Requirements: Raspberry Pi 3
"""

__author__ = "Alberto Occelli"
__copyright__ = "Copyright 2023,"
__credits__ = ["Alberto Occelli"]
__license__ = "MIT"
__version__ = "1.7.0 - Blackbird"
__maintainer__ = "Alberto Occelli"
__email__ = "albertoccelli@gmail.com"
__status__ = "Dev"

import RPi.GPIO as GPIO
import time
import os
import subprocess

from config import *
from utils import curwd, audio_prompt, print_datetime, get_sinks

GPIO.setup(button_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(button_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

running = False

hold = 1

def get_running():
    run = subprocess.Popen(["systemctl", "--user", "status", "player.service"], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    run.wait()
    stdout, stderr = run.communicate()
    status = str(stdout).split("Active: ")[-1].split("\\n")[0]
    if "inactive" in status.lower():
        return False
    else:
        if "active" in status.lower():
            return True
        else:
            return None

def toggle_standby(channel):
    global running
    pressed_time = time.time()
    while GPIO.input(button_1) == GPIO.HIGH:
        if GPIO.input(button_2) == GPIO.HIGH:
            reboot()
            return
        elapsed = time.time()-pressed_time
        #print(elapsed)
        if elapsed >= hold:
            print(elapsed)
            standby()
            return


def reboot_button(channel):
    while GPIO.input(button_2) == GPIO.HIGH:
        if GPIO.input(button_2) == GPIO.HIGH and GPIO.input(button_1) == GPIO.HIGH:
            reboot()
            return


def reboot():
    time_pressed = time.time()
    elapsed = 0
    while (GPIO.input(button_2) == GPIO.HIGH or GPIO.input(button_1) == GPIO.HIGH) and elapsed <= 5:
        elapsed = time.time() - time_pressed
        time.sleep(0.1)
        pass
    running = get_running()
    print(running)
    if elapsed > 5:
        if not running:
            print_datetime("Reset bluetooth")
            os.system("sudo systemctl start bluetooth")
            audio_prompt(f"{curwd}/prompts/eng/reset_bt.wav")
            time.sleep(1)
            os.system(f"python {curwd}/reset_bt.py")
            time.sleep(2)
            #os.system("sudo reboot now")
            standby()

def standby():
    global running
    running = get_running()
    if running:
        running = False
        print_datetime("Stopping demo")
        os.system("systemctl --user stop player")
        audio_prompt(f"{curwd}/prompts/eng/standby.wav")
        time.sleep(0.1)
        os.system("sudo systemctl stop bluetooth")
    else:
        print_datetime("Starting demo")
        os.system("systemctl --user start player")
        #os.system("sudo systemctl start bluetooth")
        running = True
        time.sleep(3)


def boot():
    global running
    running = get_running()
    if running:
        running = False
        print_datetime("Stopping demo")
        os.system("systemctl --user stop player")
        audio_prompt(f"{curwd}/prompts/eng/standby.wav")
        time.sleep(0.1)
        os.system("sudo systemctl stop bluetooth")
        time.sleep(4)
    else:
        print_datetime("Checking system integrity")
        os.system("systemctl --user start watchdog")
        os.system("sudo systemctl stop bluetooth")
        running = True

GPIO.add_event_detect(button_1, GPIO.RISING, callback=toggle_standby, bouncetime=200)
GPIO.add_event_detect(button_2, GPIO.RISING, callback=reboot_button, bouncetime=200)


def main():
    global running
    print_datetime("+++ WELCOME TO THE SANMARCO INSTORE DEMO +++")
    print_datetime(f"Version: {__version__}")
    os.system(f"pactl set-sink-volume 0 {fr_volume}%")
    os.system("systemctl --user stop player")
    p_sinks = 1
    audio_prompt(f"{curwd}/prompts/eng/please_wait.wav")
    boot()
    try:
        while True:
            n_sinks = len(get_sinks())
            #print(f"{running}\t{n_sinks}\t{p_sinks}")
            if running and n_sinks == 1 and p_sinks != 1:
                standby()
            time.sleep(1)
            p_sinks = n_sinks
            pass
    except KeyboardInterrupt:
        GPIO.cleanup()
        return


main()
os.system("systemctl --user stop player")
