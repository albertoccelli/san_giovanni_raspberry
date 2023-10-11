#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
SM demo: control the reproducing of 2 audio streams via BT and Jack. Controls are done by external
sensors and buttons/rotary encoders

Changelogs:
1.3.0 - added support for multiple encoders
1.2.0 - multilanguage support added
1.1.0 - playlist automatically sorts alphabetically the tracks; index in YAML file starts with 1
1.0.0 - first release

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
import RPi.GPIO as GPIO

from sensor import DistanceSensor
from utils import print_datetime

bg_vol_button = 27
bg_vol_dt_pin = 17
bg_vol_clk_pin = 18
echo_pin = 24
trig_pin = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(bg_vol_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(bg_vol_dt_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(bg_vol_clk_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

if __name__ == "__main__":
    from utils import get_sinks
    import os
    from player import Player
    from utils import load_config, set_spkr_volume_max, curwd
    from config import *

    # configuration file
    config_file = f"/{curwd}/config.yaml"
    d_sensor_enabled = load_config(config_file).get("distance_sensor_enabled")  # load distance sensor configuration

    # Buttons and encoders
    # Background volume encoder
    bg_vol_button = load_config(config_file).get("bg_vol_button")  # pause/play button
    bg_vol_dt_pin = load_config(config_file).get("bg_vol_dt_pin")  # rotary encoder DT pin
    bg_vol_clk_pin = load_config(config_file).get("bg_vol_clk_pin")  # rotary encoder CLK pin
    # Background track encoder
    bg_tr_button = load_config(config_file).get("bg_tr_button")  # pause/play button
    bg_tr_dt_pin = load_config(config_file).get("bg_tr_dt_pin")  # rotary encoder DT pin
    bg_tr_clk_pin = load_config(config_file).get("bg_tr_clk_pin")  # rotary encoder CLK pin
    # Front volume encoder
    fr_vol_button = load_config(config_file).get("fr_vol_button")  # pause/play button
    fr_vol_dt_pin = load_config(config_file).get("fr_vol_dt_pin")  # rotary encoder DT pin
    fr_vol_clk_pin = load_config(config_file).get("fr_vol_clk_pin")  # rotary encoder CLK pin
    # Front track encoder
    fr_tr_button = load_config(config_file).get("fr_tr_button")  # pause/play button
    fr_tr_dt_pin = load_config(config_file).get("fr_tr_dt_pin")  # rotary encoder DT pin
    fr_tr_clk_pin = load_config(config_file).get("fr_tr_clk_pin")  # rotary encoder CLK pin

    # Sensor
    echo_pin = load_config(config_file).get("echo_pin")  # sensor echo pin
    trig_pin = load_config(config_file).get("trig_pin")  # sensor trigger pin

    # Player settings
    start_track = load_config(config_file).get("start_track") - 1  # start track
    vol_step = load_config(config_file).get("volume_steps")  # volume steps
    bt_volume = load_config(config_file).get("bt_volume")  # starting volume
    lang = load_config(config_file).get("lang")  # language

    # read audio files from folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if lang:
        voice_path = f"{script_dir}/media/front/{lang}/"
    else:
        voice_path = f"{script_dir}/media/front/"
    bg_path = f"{script_dir}/media/neck/"
    voice_playlist = [f"{voice_path}{f}" for f in os.listdir(voice_path) if os.path.isfile(os.path.join(voice_path, f))]
    voice_playlist.sort()
    bg_playlist = [f"{bg_path}{f}" for f in os.listdir(bg_path) if os.path.isfile(os.path.join(bg_path, f))]
    bg_playlist.sort()

    # make sure that the paplay service is not suspended
    subprocess.Popen(["pactl", "suspend-sink", "0"])

    print_datetime("Front playlist:")
    for t in voice_playlist:
        print_datetime(f"\t{t}")
    print_datetime("Neck playlist: ")
    for t in bg_playlist:
        print_datetime(f"\t{t}")

    # initiate players
    # make sure that the bt device is ready to play:
    timeout = 5
    start = time.time()
    while True:
        audio_sinks = get_sinks()
        if len(audio_sinks) == 2:
            break
        print_datetime("SM Demo:\tBT device not found. Please wait...")
        if (time.time()-start) >= timeout:
            print_datetime("SM Demo:\tTimeout!")
            quit()
        time.sleep(0.5)

    # Set volume of neckband to max
    print_datetime("SM Demo:\tsetting neckband to max")
    set_spkr_volume_max()
    print_datetime("SM Demo:\tBT volume set to max")

    # initializing bluetooth player
    bluetooth = Player(audio_sinks[1])
    bluetooth.load(bg_playlist)
    bluetooth.current_index = start_track
    bluetooth.set_volume(bt_volume)
    bluetooth.play()
    # initializing jack player
    jack = Player(audio_sinks[0])
    jack.load(voice_playlist)
    jack.current_index = start_track
    jack.play()

    # Front volume encoder
    def fr_vol_button_pressed(channel):
        print_datetime("SM Demo:\tfront volume button pressed")
        jack.toggle_mute()

    def fr_vol_rotation(channel):
        if GPIO.input(fr_vol_dt_pin) == GPIO.input(fr_vol_clk_pin):
            print_datetime("SM Demo:\tfront volume rotary encoder clockwise")
            jack.raise_volume(step=vol_step, kind="perc")
        else:
            print_datetime("SM Demo:\tfront volume rotary encoder counterclockwise")
            jack.lower_volume(step=vol_step, kind="perc")

    # Front track encoder
    def fr_tr_button_pressed(channel):
        print_datetime("SM Demo:\tfront track button pressed")
        jack.toggle_play_pause()

    def fr_tr_rotation(channel):
        if GPIO.input(fr_tr_dt_pin) == GPIO.input(fr_tr_clk_pin):
            print_datetime("SM Demo:\tfront track rotary encoder clockwise")
            jack.next_track()
        else:
            print_datetime("SM Demo:\tfront track rotary encoder counterclockwise")
            jack.prev_track()

    # Background (neckband) volume encoder
    def bg_vol_button_pressed(channel):
        print_datetime("SM Demo:\tbackground volume button pressed")
        bluetooth.toggle_mute()

    def bg_vol_rotation(channel):
        if GPIO.input(bg_vol_dt_pin) == GPIO.input(bg_vol_clk_pin):
            print_datetime("SM Demo:\tbackground volume rotary encoder clockwise")
            bluetooth.raise_volume(step=vol_step, kind="perc")
        else:
            print_datetime("SM Demo:\tbacground volume rotary encoder counterclockwise")
            bluetooth.lower_volume(step=vol_step, kind="perc")

    # Front track encoder
    def bg_tr_button_pressed(channel):
        print_datetime("SM Demo:\tbackground track button pressed")
        bluetooth.toggle_play_pause()

    def bg_tr_rotation(channel):
        if GPIO.input(bg_tr_dt_pin) == GPIO.input(bg_tr_clk_pin):
            print_datetime("SM Demo:\tbackground track rotary encoder clockwise")
            bluetooth.next_track()
        else:
            print_datetime("SM Demo:\tbackground track rotary encoder counterclockwise")
            bluetooth.prev_track()

    # Sensor
    def distance_pause():
        print_datetime("SM Demo:\tUser too far away: pause")
        bluetooth.pause()
        jack.pause()


    def distance_resume():
        print_datetime("SM Demo:\tUser detected: resume")
        bluetooth.resume()
        jack.resume()


    # define sensors/button detect functions
    GPIO.add_event_detect(fr_vol_button, GPIO.FALLING, callback=fr_vol_button_pressed, bouncetime=150)
    GPIO.add_event_detect(fr_vol_dt_pin, GPIO.BOTH, callback=fr_vol_rotation, bouncetime=150)
    GPIO.add_event_detect(fr_tr_button, GPIO.FALLING, callback=fr_tr_button_pressed, bouncetime=150)
    GPIO.add_event_detect(fr_tr_dt_pin, GPIO.BOTH, callback=fr_tr_rotation, bouncetime=150)
    GPIO.add_event_detect(bg_vol_button, GPIO.FALLING, callback=bg_vol_button_pressed, bouncetime=150)
    GPIO.add_event_detect(bg_vol_dt_pin, GPIO.BOTH, callback=bg_vol_rotation, bouncetime=150)
    GPIO.add_event_detect(bg_tr_button, GPIO.FALLING, callback=bg_tr_button_pressed, bouncetime=150)
    GPIO.add_event_detect(bg_tr_dt_pin, GPIO.BOTH, callback=bg_tr_rotation, bouncetime=150)

    print_datetime(f"SM Demo:\tDistance sensor status={d_sensor_enabled}")
    if d_sensor_enabled:
        print_datetime("SM Demo:\tSensor started")
        d_sensor = DistanceSensor(trig_pin, echo_pin, on_posedge_callback=distance_pause,
                                  on_negedge_callback=distance_resume)
        d_sensor.threshold = load_config(config_file).get("threshold")
        d_sensor.start_measuring()

    # the main function
    def main():
        try:
            print_datetime("SM_Demo:\tDemo started...")
            while True:
                if len(get_sinks()) < 2:
                    print_datetime("SM Demo:\tFatal: lost connection")
                    subprocess.Popen(["pactl", "suspend-sink", "0"])
                    bluetooth.stop()
                    jack.stop()
                    subprocess.Popen(["killall", "paplay"])
                    print_datetime("SM_Demo:\tDemo interrupted")
                    return
                time.sleep(1)

        except KeyboardInterrupt:
            subprocess.Popen(["pactl", "suspend-sink", "0"])
            killall = subprocess.Popen(["killall", "paplay"])
            killall.wait()
            GPIO.cleanup()


    main()
