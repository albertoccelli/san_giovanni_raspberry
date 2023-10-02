#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
SM demo: control the reproducing of 2 audio streams via BT and Jack. Controls are done by external
sensors and buttons/rotary encoders

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
import RPi.GPIO as GPIO

from sensor import DistanceSensor
from utils import print_datetime

button_pin = 27
dt_pin = 17
clk_pin = 18
echo_pin = 24
trig_pin = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dt_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(clk_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

if __name__ == "__main__":
    from utils import get_sinks
    import os
    from player import Player
    from utils import load_config, set_spkr_volume_max, curwd

    # configuration file
    config_file = f"/{curwd}/config.yaml"
    d_sensor_enabled = load_config(config_file).get("distance_sensor_enabled")  # load distance sensor configuration
    button_pin = load_config(config_file).get("button_pin")  # pause/play button
    dt_pin = load_config(config_file).get("dt_pin")  # rotary encoder DT pin
    clk_pin = load_config(config_file).get("clk_pin")  # rotary encoder CLK pin
    echo_pin = load_config(config_file).get("echo_pin")  # sensor echo pin
    trig_pin = load_config(config_file).get("trig_pin")  # sensor trigger pin
    start_track = load_config(config_file).get("start_track")  # start track
    vol_step = load_config(config_file).get("volume_steps")  # volume steps
    bt_volume = load_config(config_file).get("bt_volume")  # starting volume

    # read audio files from folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    voice_path = f"{script_dir}/media/front/"
    bg_path = f"{script_dir}/media/neck/"
    voice_playlist = [f"{voice_path}{f}" for f in os.listdir(voice_path) if os.path.isfile(os.path.join(voice_path, f))]
    bg_playlist = [f"{bg_path}{f}" for f in os.listdir(bg_path) if os.path.isfile(os.path.join(bg_path, f))]
    voice_playlist = bg_playlist

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

    # defining control functions
    def toggle_play_pause():
        if bluetooth.playing:
            bluetooth.pause()
            jack.pause()
        else:
            if bluetooth.stopped:
                bluetooth.play()
                jack.play()
            else:
                bluetooth.resume()
                jack.resume()


    def btn_1_pressed(channel):
        print_datetime("SM Demo:\tbutton 1 pressed")
        toggle_play_pause()


    def rotation_1_callback(channel):
        if GPIO.input(dt_pin) == GPIO.input(clk_pin):
            print_datetime("SM Demo:\trotary encoder clockwise")
            bluetooth.next_track()
            jack.next_track()
        else:
            print_datetime("SM Demo:\trotary encoder counterclockwise")
            bluetooth.prev_track()
            jack.prev_track()

    def rotation_2_callback(channel):
        if GPIO.input(dt_pin) == GPIO.input(clk_pin):
            print_datetime("SM Demo:\trotary encoder clockwise")
            bluetooth.raise_volume(step=vol_step, kind="perc")
        else:
            print_datetime("SM Demo:\trotary encoder counterclockwise")
            bluetooth.lower_volume(step=vol_step, kind="perc")


    def distance_pause():
        print_datetime("SM Demo:\tUser too far away: pause")
        bluetooth.pause()
        jack.pause()


    def distance_resume():
        print_datetime("SM Demo:\tUser detected: resume")
        bluetooth.resume()
        jack.resume()


    # define sensors/button detect functions
    # button
    GPIO.add_event_detect(button_pin, GPIO.FALLING, callback=btn_1_pressed, bouncetime=150)
    # rotary encoder
    GPIO.add_event_detect(dt_pin, GPIO.BOTH, callback=rotation_2_callback, bouncetime=150)
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
