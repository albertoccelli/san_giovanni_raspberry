#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Player class for Raspberry Pi3. Can set up audio sink and play/pause/stop the reproducing of WAV files

Changelogs:
1.6.0 - adjust left-right volume separatedly
1.5.0 - added shuffle mode
1.4.0 - repeat all function (cycle among all tracks)
1.3.1 - bugfix on loop function
1.3.0 - variable to set/unset loop
1.2.0 - set player's boundaries
1.1.2 - fixed not unmuting when adjusting volume
1.1.1 - verbose mute function
1.1.0 - added mute function and toggle play/pause
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

import subprocess
import time
import threading
import RPi.GPIO as GPIO
import random

from utils import print_datetime, get_volume

button_pin = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)


class Player:

    def __init__(self, sink):
        print_datetime(f"{sink}: loading player")
        self.audio_thread = None
        self.sink = sink
        self.audio_process = None
        self.current_index = 0
        self.volume = 0
        self.playlist = None
        self.current_track = None
        self.playing = False
        self.stopped = True
        self.muted = [False, False]
        self.get_vol()
        self.repeat_one = False
        self.repeat_all = False
        self.shuffle = False

    def get_vol(self):
        self.volume = get_volume(self.sink)
        return

    def set_volume(self, vol_level, um="perc", mode="both"):
        set_vol = None
        p_volume = f"{int(self.volume)}"
        if mode == "both":
            self.muted = [False, False]
            self.volume = vol_level
        if um == "perc":
            vol_level = f"{vol_level}%"
            p_volume = f"{p_volume}%"
        elif um == "db":
            vol_level = f"{vol_level}db"
            p_volume = f"{p_volume}db"
        if mode == "both":
            print_datetime(f"{self.sink}: setting volume to {vol_level}")
            set_vol = subprocess.Popen(["pactl", "set-sink-volume", self.sink, vol_level],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        elif mode == "left":
            print(vol_level)
            print(p_volume)
            print_datetime(f"{self.sink}: setting left volume to {vol_level}")
            set_vol = subprocess.Popen(["pactl", "set-sink-volume", self.sink, vol_level, p_volume],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        elif mode == "right":
            print_datetime(f"{self.sink}: setting right volume to {vol_level}")
            set_vol = subprocess.Popen(["pactl", "set-sink-volume", self.sink, p_volume, vol_level],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        set_vol.wait()
        # self.get_vol()
        return

    def on_reproduction_end(self):
        # print_datetime(f"{self.sink}: reproduction ended")
        pass

    def mute(self, target="both"):
        if target == "both":
            print_datetime(f"{self.sink}: mute")
            mute = subprocess.Popen(["pactl", "set-sink-mute", self.sink, "1"],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.muted = [True, True]
            mute.wait()
        elif target == "left":
            self.set_volume("0", mode="left")
            self.muted[0] = True
        elif target == "right":
            self.set_volume("0", mode="right")
            self.muted[1] = True
        return

    def unmute(self):
        print_datetime(f"{self.sink}: unmute")
        unmute = subprocess.Popen(["pactl", "set-sink-mute", self.sink, "0"],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        unmute.wait()
        self.muted = [False, False]
        adjust_channels = subprocess.Popen(["pactl", "set-sink-volume", self.sink, self.volume],
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        adjust_channels.wait()
        return

    def toggle_mute(self):
        if self.muted:
            self.unmute()
        elif not self.muted:
            self.mute()

    def raise_volume(self, step=10, um="perc", target="both"):
        set_vol = None
        self.volume += step
        if self.muted[0] and self.muted[1]:
            self.unmute()
        if um == "perc":
            step = f"+{step}%"
            mute = "+0%"
        elif um == "db":
            step = f"+{step}db"
            mute = "+0db"
        else:
            mute = "+0"
        print_datetime(f"{self.sink}: raising volume by {step}")
        if target == "both" and not self.muted[0] and not self.muted[1]:
            set_vol = subprocess.Popen(["pactl", "set-sink-volume", self.sink, step],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        elif target == "left" or self.muted[1]:
            set_vol = subprocess.Popen(["pactl", "set-sink-volume", self.sink, step, mute],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        elif target == "right" or self.muted[0]:
            set_vol = subprocess.Popen(["pactl", "set-sink-volume", self.sink, mute, step],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        set_vol.wait()
        return

    def lower_volume(self, step=10, um="perc", target="both"):
        set_vol = None
        self.volume -= step
        if self.muted[0] and self.muted[1]:
            self.unmute()
        if um == "perc":
            step = f"-{step}%"
            mute = "-0%"
        elif um == "db":
            step = f"-{step}db"
            mute = "-0db"
        else:
            mute = "-0"
        print_datetime(f"{self.sink}: lowering volume by {step}")
        if target == "both" and not self.muted[0] and not self.muted[1]:
            set_vol = subprocess.Popen(["pactl", "set-sink-volume", self.sink, step],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        elif target == "left" or self.muted[1]:
            set_vol = subprocess.Popen(["pactl", "set-sink-volume", self.sink, step, mute],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        elif target == "right" or self.muted[0]:
            set_vol = subprocess.Popen(["pactl", "set-sink-volume", self.sink, mute, step],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        set_vol.wait()
        return

    def load(self, playlist):
        self.playlist = playlist
        if self.shuffle:
            random.shuffle(self.playlist)
        self.current_track = self.playlist[self.current_index]
        return self.playlist

    def play_audio(self, filename=None, repeat_one=False, repeat_all=False):
        self.repeat_all = repeat_all
        self.repeat_one = repeat_one
        self.playing = True
        self.stopped = False
        self.current_track = self.playlist[self.current_index]
        if filename is not None:
            self.current_track = filename
        while self.playing:
            try:
                print_datetime(f"{self.sink}: playing {self.current_track}|Repeat one={self.repeat_one}; "
                               f"Repeat all={self.repeat_all}")
                self.audio_process = subprocess.Popen(["paplay", f"--device={self.sink}", self.current_track],
                                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                stdout, stderr = self.audio_process.communicate()
                if stderr:
                    print_datetime(f"{self.sink}: error reproducing audio: {stderr}")
                    break
                self.audio_process.wait()
                if not repeat_one:
                    self.current_index = self.current_index + 1
                    if self.current_index >= len(self.playlist):
                        self.current_index = 0
                        if not repeat_all:
                            self.playing = False
                            break
                    self.current_track = self.playlist[self.current_index]
                    print(f"NEXT TRACK: {self.current_track}")
            except Exception as error:
                print_datetime(f"{self.sink}: error reproducing audio: {error}")
                break
        self.stop()
        print_datetime(f"{self.sink}: end of reproduction")
        self.on_reproduction_end()

    def play(self, repeat_one=False, repeat_all=False):
        self.audio_thread = threading.Thread(target=self.play_audio, args=(None, repeat_one, repeat_all))
        self.audio_thread.daemon = True
        self.audio_thread.start()

    def pause(self):
        self.playing = False
        print_datetime(f"{self.sink}: pause")
        # self.audio_process.send_signal(subprocess.signal.SIGSTOP)
        pause = subprocess.Popen(["pactl", "suspend-sink", self.sink, "1"])
        pause.wait()

    def resume(self):
        self.playing = True
        print_datetime(f"{self.sink}: resume")
        # self.audio_process.send_signal(subprocess.signal.SIGCONT)
        resume = subprocess.Popen(["pactl", "suspend-sink", self.sink, "0"])
        resume.wait()

    def toggle_play_pause(self):
        if self.playing:
            self.pause()
        else:
            if self.stopped:
                self.play()
            else:
                self.resume()

    def stop(self):
        try:
            self.playing = False
            self.stopped = True
            self.audio_process.terminate()
            self.audio_thread.join()
            print_datetime(f"{self.sink}: Stop")
        except Exception as exception:
            if "nonetype" in str(exception).lower():
                print_datetime(f"{self.sink}: no audio to stop")

    def next_track(self, repeat_one=None, repeat_all=None):
        if repeat_one is None:
            repeat_one = self.repeat_one
        if repeat_all is None:
            repeat_all = self.repeat_all
        self.stop()
        self.current_index += 1
        if self.current_index >= len(self.playlist):
            self.current_index = 0
        self.current_track = self.playlist[self.current_index]
        print_datetime(f"{self.sink}: next track -> {self.current_track}")
        self.play(repeat_one, repeat_all)

    def prev_track(self):
        self.stop()
        self.current_index -= 1
        if self.current_index < 0:
            self.current_index = len(self.playlist) - 1
        self.current_track = self.playlist[self.current_index]
        print_datetime(f"{self.sink}: previous track <- {self.current_track}")
        self.play(self.repeat_one)


def main():
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        GPIO.cleanup()


if __name__ == "__main__":

    from utils import get_sinks
    import os

    # read audio files from folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    voice_path = f"{script_dir}/media/front/ita/"
    bg_path = f"{script_dir}/media/neck/"
    voice_playlist = [f"{voice_path}{f}" for f in os.listdir(voice_path) if os.path.isfile(os.path.join(voice_path, f))]
    print_datetime(voice_playlist)
    bg_playlist = [f"{bg_path}{f}" for f in os.listdir(bg_path) if os.path.isfile(os.path.join(bg_path, f))]

    # get sink information
    while True:
        try:
            bt_sink = get_sinks()[1]
            jack_sink = get_sinks()[0]
            break
        except Exception as e:
            print(e)
            pass
        time.sleep(3)


    # initialize players
    class NewPlayer(Player):
        def on_reproduction_end(self):
            print("OVERRIDDEN FUNCTION")


    bluetooth = Player(bt_sink)
    jack = Player(jack_sink)


    # initialize GPIOs
    def bt_next(channel):
        bluetooth.next_track()


    def bt_toggle_pause(channel):
        if bluetooth.playing:
            bluetooth.pause()
        else:
            bluetooth.resume()


    GPIO.add_event_detect(button_pin, GPIO.FALLING, callback=bt_next, bouncetime=200)
    # GPIO.add_event_detect(button_pin, GPIO.FALLING, callback=bt_toggle_pause, bouncetime=200)

    # setup player
    bluetooth.load(bg_playlist)
    bluetooth.play(repeat_one=True)
    jack.load(voice_playlist)
    jack.play()
    print_datetime(voice_playlist)
    # main loop function
    main()
