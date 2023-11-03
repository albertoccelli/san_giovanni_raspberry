#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Automatically checks for new usb drives to perform the update of the SM Demo Software

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
import threading
import RPi.GPIO as GPIO

TRIG_PIN = 23
ECHO_PIN = 24

treshold = 100

class DistanceSensor:
    def __init__(self, trigpin, echopin, on_posedge_callback=None, on_negedge_callback=None):
        self.trigpin = trigpin
        self.echopin = echopin
        self.on_posedge_callback = on_posedge_callback
        self.on_negedge_callback = on_negedge_callback
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(trigpin, GPIO.OUT)
        GPIO.setup(echopin, GPIO.IN)
        self.distance = None
        self.threshold = 50
        self.running = False
        self.lock = threading.Lock()

    def get_distance(self):
        pulse_end, pulse_start = None, None
        GPIO.output(self.trigpin, GPIO.HIGH)
        time.sleep(0.00002)
        GPIO.output(self.trigpin, GPIO.LOW)
        while GPIO.input(self.echopin) == GPIO.LOW:
            pulse_start = time.time()
        while GPIO.input(self.echopin) == GPIO.HIGH:
            pulse_end = time.time()
        pulse_duration = pulse_end - pulse_start
        distance = (pulse_duration * 34300) / 2
        return distance

    def measure_distance(self):
        p_distance = self.get_distance()
        while self.running:
            self.lock.acquire()
            self.distance = self.get_distance()
            print(self.distance)
            if self.distance > self.threshold > p_distance:
                print("Posedge")
                if self.on_posedge_callback:
                    self.on_posedge_callback()
            elif self.distance < self.threshold < p_distance:
                print("Negedge")
                if self.on_negedge_callback:
                    self.on_negedge_callback()
            self.lock.release()
            p_distance = self.distance
            time.sleep(1)

    def start_measuring(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.measure_distance)
            self.thread.daemon = True
            self.thread.start()

    def stop_measurement(self):
        if self.running:
            self.running = False
            self.thread.join()


if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIG_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)

    def custom_cb():
        print("OCHEI")


    sensor = DistanceSensor(TRIG_PIN, ECHO_PIN, on_posedge_callback=custom_cb, on_negedge_callback=custom_cb)

    try:
        sensor.start_measuring()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sensor.stop_measurement()
        GPIO.cleanup()
