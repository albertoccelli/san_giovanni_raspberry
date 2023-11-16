import RPi.GPIO as GPIO
import time
import os


from config import *

GPIO.setup(button_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
running = False

def toggle_standby(channel):
    pressed_time = time.time()
    while GPIO.input(button_1) == GPIO.HIGH:
        elapsed = time.time()-pressed_time
        if elapsed >= 4:
            standby()
            return

def standby():
    global running
    if running:
        print("Stopping demo")
        os.system("systemctl --user stop player")
    else:
        print("Starting demo")
        os.system("systemctl --user start player")
    running = not running

GPIO.add_event_detect(button_1, GPIO.RISING, callback=toggle_standby, bouncetime=200)


def main():
    try:
        while True:
            time.sleep(10)
            pass
    except KeyboardInterrupt:
        GPIO.cleanup()

main()


