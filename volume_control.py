#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Volume control: creates a routine to change the global volume of the raspberry with the rotary encoder.
This is intended to be a parallel routine with the sm demo

Changelogs:
1.0.0 - first release

Requirements: Raspberry Pi 3
"""

import subprocess
import RPi.GPIO as GPIO

from config import *
from utils import get_sinks, print_datetime, get_volume, get_mute

rpi_sink = get_sinks()[0]
rpi_mute = False


def fr_vol_button_pressed(channel):
    print_datetime("SM Demo:\tfront volume button pressed")
    mute_status = get_mute()
    toggle = "0"
    if mute_status:
        toggle = "0"
    else:
        toggle = "1"
    set_mute = subprocess.Popen(["pactl", "set-sink-mute", rpi_sink, toggle],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    set_mute.wait()


def fr_vol_rotation(channel):
    step = ""
    if GPIO.input(fr_vol_dt_pin) == GPIO.input(fr_vol_clk_pin):
        print_datetime("SM Demo:\tfront volume rotary encoder clockwise")
        if vol_step_um == "perc":
            step = f"+{vol_step}%"
        elif vol_step_um == "db":
            step = f"+{vol_step}db"
        print_datetime(f"{rpi_sink}: \tRaising volume by {step}")
        set_vol = subprocess.Popen(["pactl", "volume", rpi_sink, step],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        set_vol.wait()
    else:
        print_datetime("SM Demo:\tfront volume rotary encoder counterclockwise")
        if vol_step_um == "perc":
            step = f"-{vol_step}%"
        elif vol_step_um == "db":
            step = f"-{vol_step}db"
        print_datetime("SM Demo:\tfront volume rotary encoder clockwise")
        print_datetime(f"{rpi_sink}: \tLowering volume by {step}")
        set_vol = subprocess.Popen(["pactl", "volume", rpi_sink, step],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        set_vol.wait()


# enable the functions related to the encoders
GPIO.add_event_detect(fr_vol_button, GPIO.FALLING, callback=fr_vol_button_pressed, bouncetime=200)
GPIO.add_event_detect(fr_vol_dt_pin, GPIO.BOTH, callback=fr_vol_rotation, bouncetime=150)
