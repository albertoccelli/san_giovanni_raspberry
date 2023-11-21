#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Player class for Raspberry Pi3. Can set up audio sink and play/pause/stop the reproducing of WAV files

Changelogs:
1.6.0 - ACROSS THE UNIVERSE - first stable release

Requirements: Raspberry Pi 3
"""

__author__ = "Alberto Occelli"
__copyright__ = "Copyright 2023,"
__credits__ = ["Alberto Occelli"]
__license__ = "MIT"
__version__ = "1.6.0 - Across the universe"
__maintainer__ = "Alberto Occelli"
__email__ = "albertoccelli@gmail.com"
__status__ = "Dev"

import RPi.GPIO as GPIO
import time
import os


from config import *
from utils import curwd, audio_prompt, print_datetime

GPIO.setup(button_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(button_5, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
running = False


def toggle_standby(channel):
    pressed_time = time.time()
    while GPIO.input(button_1) == GPIO.HIGH:
        if GPIO.input(button_5) == GPIO.HIGH:
            reboot()
            return
        elapsed = time.time()-pressed_time
        if elapsed >= 4:
            standby()
            return


def reboot_button(channel):
    while GPIO.input(button_5) == GPIO.HIGH:
        if GPIO.input(button_5) == GPIO.HIGH and GPIO.input(button_1) == GPIO.HIGH:
            reboot()
            return


def reboot():
    time_pressed = time.time()
    elapsed = 0
    while (GPIO.input(button_5) == GPIO.HIGH or GPIO.input(button_1) == GPIO.HIGH) and elapsed <= 5:
        elapsed = time.time() - time_pressed
        time.sleep(0.1)
        pass
    if elapsed > 5:
        print_datetime("REBOOT")
        audio_prompt(f"{curwd}/prompts/{lang}/reboot.wav")
        os.system("sudo reboot now")


def standby():
    global running
    if running:
        print_datetime("Stopping demo")
        os.system("systemctl --user stop player")
        os.system("sudo systemctl stop bluetooth")
        audio_prompt(f"{curwd}/prompts/eng/standby.wav")
    else:
        print_datetime("Starting demo")
        os.system("systemctl --user start player")
        os.system("sudo systemctl start bluetooth")
    running = not running


GPIO.add_event_detect(button_1, GPIO.RISING, callback=toggle_standby, bouncetime=200)
GPIO.add_event_detect(button_5, GPIO.RISING, callback=reboot_button, bouncetime=200)


def main():
    print_datetime("+++ WELCOME TO THE SANMARCO INSTORE DEMO +++")
    print_datetime(f"Version: {__version__}")
    os.system(f"pactl set-sink-volume 0 {fr_volume}%")
    os.system("systemctl --user stop player")
    audio_prompt(f"{curwd}/prompts/startup.wav")
    try:
        while True:
            time.sleep(10)
            pass
    except KeyboardInterrupt:
        GPIO.cleanup()
        return


main()
os.system("systemctl --user stop player")
