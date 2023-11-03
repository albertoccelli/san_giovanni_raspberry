#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Configuration script for SM Demo. Configures the GPIOs

Changelogs:
1.3.0 - removed encoders
1.2.0 - support for multilanguage
1.1.0 - volume unit of measure added
1.0.0 - first release

Requirements: Raspberry Pi 3
"""

__author__ = "Alberto Occelli"
__copyright__ = "Copyright 2023,"
__credits__ = ["Alberto Occelli"]
__license__ = "MIT"
__version__ = "1.2.0"
__maintainer__ = "Alberto Occelli"
__email__ = "albertoccelli@gmail.com"
__status__ = "Dev"

import RPi.GPIO as GPIO
from utils import load_config, curwd

# configuration file
config_file = f"/{curwd}/config.yaml"
d_sensor_enabled = load_config(config_file).get("distance_sensor_enabled")  # load distance sensor configuration

# Language
lang = load_config(config_file).get("lang")  # language

# Buttons
# Front track button
fr_tr_button = load_config(config_file).get("fr_tr_button")
# Background track button
bg_tr_button = load_config(config_file).get("bg_tr_button")
# Front volume up button
fr_vol_up_button = load_config(config_file).get("fr_vol_up_button")
# Front volume down button
fr_vol_down_button = load_config(config_file).get("fr_vol_up_button")


start_track = load_config(config_file).get("start_track") - 1  # start track
vol_step_um = load_config(config_file).get("volume_steps_um")  # unit of measure for volume steps
vol_step = load_config(config_file).get("volume_steps")  # volume steps
bt_volume = load_config(config_file).get("bt_volume")  # starting volume
fr_volume = load_config(config_file).get("fr_volume")  # starting volume
lang = load_config(config_file).get("lang")  # language

# Setup GPIOs as inputs
GPIO.setmode(GPIO.BCM)
GPIO.setup(fr_tr_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(bg_tr_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(fr_vol_up_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(fr_vol_down_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)