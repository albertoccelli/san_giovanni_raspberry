#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
SM demo: control the reproducing of 2 audio streams via BT and Jack. Controls are done by external
sensors and buttons/rotary encoders

Changelogs:
1.8.0 - Buttons 2, 3, 4, 5 implemented
1.7.0 - button 1 implemented:
	short touch -> change language
	mid touch -> change background noise
	long touch -> turn off
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

from utils import print_datetime

if __name__ == "__main__":
    from utils import get_sinks
    import sys
    import os
    from player import Player
    import threading
    from utils import audio_prompt, load_config, set_spkr_volume_max, curwd
    from config import *

    standby = False
    langs = ["eng", "ita", "fra", "spa"]
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
#    bluetooth.play(loop=True)

    # initializing jack player
    class JackPlayer(Player):
        def on_reproduction_end(self):
            pass


    jack = JackPlayer(audio_sinks[0])
    jack.load(voice_playlist)
    jack.current_index = start_track
#    jack.play(loop=True)

    print_datetime(f"SM Demo:\tDistance sensor status={d_sensor_enabled}")

    def button_1_pressed(channel):
        elapsed = 0
        pressed_time = time.time()
        while GPIO.input(button_1) == GPIO.HIGH:
            elapsed = time.time()-pressed_time
            if elapsed >= 5:
                # long_1_press()
                return
        if elapsed <= 0.1:
            pass
        elif elapsed > 0.1 and elapsed <= 1:
            change_lang()
        elif elapsed > 1 and elapsed < 5:
            change_noise()

    def change_noise():
        if bluetooth.playing:
            bluetooth.stop()
            print_datetime("SM Demo:\tmid button press")
            next_index = bluetooth.current_index + 1
            if next_index >= len(bg_playlist):
                next_index = 0
            # audio_prompt(f"{curwd}/prompts/eng/noise_{next_index+1}.wav")
            bluetooth.play_audio(filename=f"{curwd}/prompts/eng/noise_{next_index+1}.wav")
            print(f"{next_index+1}/{len(bg_playlist)}")
            bluetooth.next_track()

    def change_lang():
        to_resume = False
        if jack.playing:
            to_resume = True
        jack.stop()
        global lang
        timer = 0
        while True:
            if timer >= 2: break
            start_time = time.time()
            next_lang_index = langs.index(lang) + 1
            if next_lang_index >= len(langs):
                next_lang_index = 0
            lang = langs[next_lang_index]
            print_datetime(f"SM Demo:\tselected language: {lang}")
            audio_prompt(f"{curwd}/prompts/{lang}/language.wav")
            while GPIO.input(button_1) == GPIO.LOW and timer <= 2:
                timer = (time.time()-start_time)
            while GPIO.input(button_1) == GPIO.HIGH:
                pass
            time.sleep(0.1)
        # start reproduction
        voice_path = f"{script_dir}/media/front/{lang}/"
        voice_playlist = [f"{voice_path}{f}" for f in os.listdir(voice_path) if os.path.isfile(os.path.join(voice_path, f))]
        voice_playlist.sort()
        jack.load(voice_playlist)
        if to_resume:
            jack.play(loop = True)

    def button_2_pressed(channel):
        p_time = time.time()
        while GPIO.input(button_2) == GPIO.HIGH:
            if GPIO.input(button_3) == GPIO.HIGH and GPIO.input(button_2) == GPIO.HIGH:
                button_23_pressed()
                return
            pass
        if time.time() - p_time > 0.05:
            if not bluetooth.playing:
                bluetooth.play(loop = True)
                bluetooth.playing = True
            else:
                bluetooth.stop()
                bluetooth.playing = False

    def button_3_pressed(channel):
        if GPIO.input(button_2) == GPIO.LOW:
            p_time = time.time()
            while GPIO.input(button_3) == GPIO.HIGH:
                pass
            if time.time() - p_time > 0.05:
                if not jack.playing:
                    jack.play(loop = True)
                else:
                    jack.stop()

    def button_4_pressed(channel):
        elapsed = 0
        pressed_time = time.time()
        while GPIO.input(button_4) == GPIO.HIGH:
            elapsed = round(time.time()-pressed_time, 2)
        if elapsed <= 0.05:
            return
        else:
            vol_down()

    def button_5_pressed(channel):
        elapsed = 0
        pressed_time = time.time()
        while GPIO.input(button_5) == GPIO.HIGH:
            elapsed = round(time.time()-pressed_time, 2)
        if elapsed <= 0.05:
            return
        else:
            vol_up()


    def vol_up(channel):
        p_time = time.time()
        while GPIO.input(button_5) == GPIO.HIGH:
            pass
        if time.time() - p_time >= 0.05:
            print("VOLUME UP")
            jack.raise_volume(step=vol_step, um=vol_step_um)

    def vol_down(channel):
        p_time = time.time()
        while GPIO.input(button_4) == GPIO.HIGH:
            pass
        if time.time() - p_time >= 0.05:
            print("VOLUME DOWN")
            jack.lower_volume(step=vol_step, um=vol_step_um)

    def button_23_pressed():
        print("SIMULTANEOUS PRESS OF 2 AND 3 BUTTON")
        while GPIO.input(button_3) == GPIO.HIGH or GPIO.input(button_2) == GPIO.HIGH:
            pass
        print("DOUBLE PRESS RELEASED")
        time.sleep(0.2)


    GPIO.add_event_detect(button_1, GPIO.RISING, callback=button_1_pressed, bouncetime=200)
    GPIO.add_event_detect(button_2, GPIO.RISING, callback=button_2_pressed, bouncetime=200)
    GPIO.add_event_detect(button_3, GPIO.RISING, callback=button_3_pressed, bouncetime=200)
    GPIO.add_event_detect(button_4, GPIO.RISING, callback=vol_down, bouncetime=150)
    GPIO.add_event_detect(button_5, GPIO.RISING, callback=vol_up, bouncetime=150)

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
                time.sleep(2)

        except KeyboardInterrupt:
            subprocess.Popen(["pactl", "suspend-sink", "0"])
            killall = subprocess.Popen(["killall", "paplay"])
            killall.wait()
            GPIO.cleanup()


    main()
