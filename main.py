import RPi.GPIO as GPIO
import time
import os


from config import *
from utils import curwd, audio_prompt

GPIO.setup(button_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(button_5, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
running = False

def toggle_standby(channel):
    pressed_time = time.time()
    while GPIO.input(button_1) == GPIO.HIGH:
        if GPIO.input(button_5) == GPIO.HIGH:
            reboot()
            return
        elapsed = time.time()-pressed_time
        if elapsed >= 4:
            standby()
            return


def reboot_button(channel):
    while GPIO.input(button_5) == GPIO.HIGH:
        if GPIO.input(button_5) == GPIO.HIGH and GPIO.input(button_1) == GPIO.HIGH:
            reboot()
            return


def reboot():
    time_pressed = time.time()
    elapsed = 0
    while (GPIO.input(button_5) == GPIO.HIGH or GPIO.input(button_1) == GPIO.HIGH) and elapsed <= 5:
        elapsed = time.time() - time_pressed
        time.sleep(0.1)
        pass
    if elapsed > 5:
        print("REBOOT")
        audio_prompt(f"{curwd}/prompts/{lang}/reboot.wav")
        os.system("sudo reboot now")

def standby():
    global running
    if running:
        print("Stopping demo")
        os.system("systemctl --user stop player")
        audio_prompt(f"{curwd}/prompts/eng/standby.wav")
    else:
        print("Starting demo")
        os.system("systemctl --user start player")
    running = not running

GPIO.add_event_detect(button_1, GPIO.RISING, callback=toggle_standby, bouncetime=200)
GPIO.add_event_detect(button_5, GPIO.RISING, callback=reboot_button, bouncetime=200)


def main():
    os.system(f"pactl set-sink-volume 0 {fr_volume}%")
    os.system("systemctl --user stop player")
    audio_prompt(f"{curwd}/prompts/startup.wav")
    try:
        while True:
            time.sleep(10)
            pass
    except KeyboardInterrupt:
        GPIO.cleanup()
        return

main()
os.system("systemctl --user stop player")
