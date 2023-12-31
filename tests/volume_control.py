#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Volume control: creates a routine to change the global volume of the raspberry with the rotary encoder.
This is intended to be a parallel routine with the sm demo

Changelogs:
1.3.2 - bugfix
1.3.1 - unmute when vol encoder is turned
1.3.0 - bt volume control added
1.2.1 - print current volume value
1.2.0 - Locks volume at minimum/maximum
1.1.0 - automatically sets volume at start
1.0.0 - first release

Requirements: Raspberry Pi 3
"""

__author__ = "Alberto Occelli"
__copyright__ = "Copyright 2023,"
__credits__ = ["Alberto Occelli"]
__license__ = "MIT"
__version__ = "1.3.1"
__maintainer__ = "Alberto Occelli"
__email__ = "albertoccelli@gmail.com"
__status__ = "Dev"

import time
import subprocess
import RPi.GPIO as GPIO
import threading

from config import *
from utils import get_sinks, print_datetime, get_volume, get_mute

rpi_sink = get_sinks()[0]
rpi_mute = False
bt_mute = False
try:
    bt_sink = get_sinks()[1]
except IndexError:
    print("No bt sink found! Bt encoder disabled")

cur_rpi_vol = 0
cur_bt_vol = 0


# Background (neckband) volume encoder
def bg_vol_button_pressed(channel):
    print_datetime("SM Demo:\tbt volume button pressed")
    try:
        mute_status = get_mute()[bt_sink]
        if mute_status:
            toggle = "0"
        else:
            toggle = "1"
        print_datetime(f"{bt_sink}:\tSet mute {toggle}")
        set_mute = subprocess.Popen(["pactl", "set-sink-mute", bt_sink, toggle],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        set_mute.wait()
    except NameError:
        print_datetime("SM Demo:\tbt not connected")

    except KeyError:
        # connection with bt is lost
        print_datetime("SM Demo:\tlost connection with bt")


def bg_vol_rotation(channel):
    global cur_bt_vol
    global bt_sink
    step = 0
    if bt_mute:
        unmute = subprocess.Popen(["pactl", "set-sink-mute", bt_sink, "0"],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        unmute.wait()
    try:
        if GPIO.input(bg_vol_dt_pin) == GPIO.input(bg_vol_clk_pin):
            pass
            print_datetime("SM Demo:\tbt volume rotary encoder clockwise")
            if cur_bt_vol == 100:
                print_datetime("SM Demo:\tbt max volume reached")
            else:
                if vol_step_um == "perc":
                    step = f"+{vol_step}%"
                elif vol_step_um == "db":
                    step = f"+{vol_step}db"
                print_datetime(f"{bt_sink}:\tRaising volume by {step}")
                set_vol = subprocess.Popen(["pactl", "set-sink-volume", bt_sink, step],
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                set_vol.wait()
        else:
            print_datetime("SM Demo:\tbt volume rotary encoder counterclockwise")
            if cur_bt_vol == 0:
                print_datetime("SM Demo:\tbt minimum volume reached")
            else:
                if vol_step_um == "perc":
                    step = f"-{vol_step}%"
                elif vol_step_um == "db":
                    step = f"-{vol_step}db"
                print_datetime(f"{bt_sink}:\tLowering volume by {step}")
                set_vol = subprocess.Popen(["pactl", "set-sink-volume", bt_sink, step],
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                set_vol.wait()
        cur_bt_vol = round(get_volume(bt_sink, "perc"))
        print_datetime(f"{bt_sink}:\tvolume {cur_bt_vol}%")

    except NameError:
        print_datetime("SM Demo:\tbt not connected")

    except KeyError:
        # connection with bt is lost
        print_datetime("SM Demo:\tlost connection with bt")


def fr_vol_button_pressed(channel):
    print_datetime("SM Demo:\tfront volume button pressed")
    mute_status = get_mute()[rpi_sink]
    if mute_status:
        toggle = "0"
    else:
        toggle = "1"
    print_datetime(f"{rpi_sink}:\tSet mute {toggle}")
    set_mute = subprocess.Popen(["pactl", "set-sink-mute", rpi_sink, toggle],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    set_mute.wait()


def fr_vol_rotation(channel):
    global cur_rpi_vol
    step = 0
    if rpi_mute:
        unmute = subprocess.Popen(["pactl", "set-sink-mute", rpi_sink, "0"],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        unmute.wait()
    if GPIO.input(fr_vol_dt_pin) == GPIO.input(fr_vol_clk_pin):
        print_datetime("SM Demo:\tfront volume rotary encoder clockwise")
        if cur_rpi_vol == 100:
            print_datetime("SM Demo:\tfront max volume reached")
        else:
            if vol_step_um == "perc":
                step = f"+{vol_step}%"
            elif vol_step_um == "db":
                step = f"+{vol_step}db"
            print_datetime(f"{rpi_sink}:\tRaising volume by {step}")
            set_vol = subprocess.Popen(["pactl", "set-sink-volume", rpi_sink, step],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            set_vol.wait()
    else:
        print_datetime("SM Demo:\tfront volume rotary encoder counterclockwise")
        if cur_rpi_vol == 0:
            print_datetime("SM Demo:\tfront minimum volume reached")
        else:
            if vol_step_um == "perc":
                step = f"-{vol_step}%"
            elif vol_step_um == "db":
                step = f"-{vol_step}db"
            print_datetime(f"{rpi_sink}:\tLowering volume by {step}")
            set_vol = subprocess.Popen(["pactl", "set-sink-volume", rpi_sink, step],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            set_vol.wait()
    cur_rpi_vol = round(get_volume(rpi_sink, "perc"))
    print_datetime(f"{rpi_sink}:\tvolume {cur_rpi_vol}%")


if __name__ == "__main__":
    # enable the functions related to the encoders
    GPIO.add_event_detect(fr_vol_button, GPIO.FALLING, callback=fr_vol_button_pressed, bouncetime=200)
    GPIO.add_event_detect(fr_vol_dt_pin, GPIO.BOTH, callback=fr_vol_rotation, bouncetime=200)
    GPIO.add_event_detect(bg_vol_button, GPIO.FALLING, callback=bg_vol_button_pressed, bouncetime=200)
    GPIO.add_event_detect(bg_vol_dt_pin, GPIO.BOTH, callback=bg_vol_rotation, bouncetime=200)
    bt_sink = None

    bt_connected = True
    print_datetime("SM Demo:\tRetrieving bluetooth sink")
    try:
        bt_sink = get_sinks()[1]
        print_datetime("SM Demo:\tDone")
        bt_connected = True
    except IndexError:
        print_datetime("SM Demo:\tBt sink not found.")
        bt_connected = False

    def check_bt():
        global bt_connected
        global bt_sink
        global bt_mute
        while True:
            if not bt_connected:
                try:
                    bt_sink = get_sinks()[1]
                    print(bt_sink)
                    # unmute bt
                    unmute = subprocess.Popen(["pactl", "set-sink-mute", bt_sink, "0"],
                                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    unmute.wait()
                    bt_mute = False
                    bt_connected = True
                except IndexError:
                    print("Cannot connect")
            time.sleep(1)


    def main():
        global bt_connected
        global bt_sink
        # Set volume at desired level (from config)
        fr_vol = 0
        bt_vol = 0
        if vol_step_um == "perc":
            fr_vol = f"{fr_volume}%"
            bt_vol = f"{bt_volume}%"
        elif vol_step_um == "db":
            fr_vol = f"{fr_volume}db"
            bt_vol = f"{bt_volume}%"
        # set rpi volume to initial level
        set_vol = subprocess.Popen(["pactl", "set-sink-volume", rpi_sink, fr_vol],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        set_vol.wait()
        # unmute rpi
        unmute = subprocess.Popen(["pactl", "set-sink-mute", rpi_sink, "0"],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        unmute.wait()
        if bt_sink:
            set_vol = subprocess.Popen(["pactl", "set-sink-volume", bt_sink, bt_vol],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            set_vol.wait()
            # unmute bt
            unmute = subprocess.Popen(["pactl", "set-sink-mute", bt_sink, "0"],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            unmute.wait()
        check_bt_thread = threading.Thread(target=check_bt)
        check_bt_thread.daemon = True
        check_bt_thread.start()

        try:
            print_datetime("SM_Demo:\tVolume control enabled")
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            GPIO.cleanup()

    main()
