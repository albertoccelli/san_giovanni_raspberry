import RPi.GPIO as GPIO
import time
from config import *

GPIO.setmode(GPIO.BCM)

DEBOUNCE_TIME = 0.2

def button_1_pressed(channel):
    pressed_time = time.time()
    while GPIO.input(button_1) == GPIO.HIGH:
        elapsed = time.time()-pressed_time
        if elapsed >= 5:
            long_1_press()
            return
    if elapsed <= 1:
        short_1_press()
    elif elapsed > 1 and elapsed < 5:
        mid_1_press()

def long_1_press():
    print("LONG PRESS")

def mid_1_press():
    print("MID PRESS")

def short_1_press():
    print("SHORT PRESS")

GPIO.add_event_detect(button_1, GPIO.RISING, callback=button_1_pressed, bouncetime=200)
#GPIO.add_event_detect(button_2, GPIO.BOTH, callback=button_2_pressed, bouncetime=150)
#GPIO.add_event_detect(button_3, GPIO.FALLING, callback=button_3_pressed, bouncetime=200)

try:
    while True:
        pass
except KeyboardInterrupt:
    pass

GPIO.cleanup()
