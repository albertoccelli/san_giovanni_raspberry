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
__version__ = "1.3.0"
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
# Button 1
button_1 = load_config(config_file).get("button_1")
# Button 2
button_2 = load_config(config_file).get("button_2")
# Button 3
button_3 = load_config(config_file).get("button_3")


start_track = load_config(config_file).get("start_track") - 1  # start track
vol_step_um = load_config(config_file).get("volume_steps_um")  # unit of measure for volume steps
vol_step = load_config(config_file).get("volume_steps")  # volume steps
bt_volume = load_config(config_file).get("bt_volume")  # starting volume
fr_volume = load_config(config_file).get("fr_volume")  # starting volume
lang = load_config(config_file).get("lang")  # language

# Setup GPIOs as inputs
GPIO.setmode(GPIO.BCM)
GPIO.setup(button_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button_3, GPIO.IN, pull_up_down=GPIO.PUD_UP)