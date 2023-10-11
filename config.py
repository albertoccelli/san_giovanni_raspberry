#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Configuration script for SM Demo. Configures the GPIOs

Changelogs:
1.0.0 - first release

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

import RPi.GPIO as GPIO
from utils import load_config, curwd

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

# Setup GPIOs as inputs
GPIO.setmode(GPIO.BCM)
GPIO.setup(bg_vol_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(bg_vol_dt_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(bg_vol_clk_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(bg_tr_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(bg_tr_dt_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(bg_tr_clk_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(fr_vol_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(fr_vol_dt_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(fr_vol_clk_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(fr_tr_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(fr_tr_dt_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(fr_tr_clk_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)