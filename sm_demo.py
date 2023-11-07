#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
SM demo: control the reproducing of 2 audio streams via BT and Jack. Controls are done by external
sensors and buttons/rotary encoders

Changelogs:
1.6.0 - bt volume handled by separate routine
1.5.0 - front volume is handled by separate routine
1.4.2 - threading for setting the bt to max volume
1.4.1 - customizable front start volume
1.4.0 - unit of measure added from config file
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
__version__ = "1.6.0"
__maintainer__ = "Alberto Occelli"
__email__ = "albertoccelli@gmail.com"
__status__ = "Dev"

import time
import subprocess
import RPi.GPIO as GPIO

from sensor import DistanceSensor
from utils import print_datetime

if __name__ == "__main__":
    from utils import get_sinks
    import os
    from player import Player
    import threading
    from utils import load_config, set_spkr_volume_max, curwd
    from config import *

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
        if (time.time() - start) >= timeout:
            print_datetime("SM Demo:\tTimeout!")
            quit()
        time.sleep(0.5)

    # Set volume of neckband to max
    set_max_thread = threading.Thread(target=set_spkr_volume_max)
    set_max_thread.start()

    # initializing bluetooth player
    bluetooth = Player(audio_sinks[1])
    bluetooth.load(bg_playlist)
    bluetooth.current_index = start_track
    bluetooth.set_volume(bt_volume)
    bluetooth.play(loop=True)

    # initializing jack player
    class JackPlayer(Player):
        def on_reproduction_end(self):
            bluetooth.stop()


    jack = JackPlayer(audio_sinks[0])
    jack.load(voice_playlist)
    jack.current_index = start_track
    jack.play(loop=True)

    print_datetime(f"SM Demo:\tDistance sensor status={d_sensor_enabled}")

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
