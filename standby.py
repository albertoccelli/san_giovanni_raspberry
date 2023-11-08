import time
import subprocess

import RPi.GPIO as GPIO

from config import button_1
from utils import audio_prompt, curwd

standby_status = False

def standby():
    global standby_status
    if not standby_status:
        print("STANDBY")
        subprocess.Popen(["systemctl", "--user", "stop", "player.service"])
        audio_prompt(f"{curwd}/prompts/eng/standby.wav")
        standby_status = True
        #subprocess.Popen(["sudo", "rfkill", "block", "wifi"])
        subprocess.Popen(["sudo", "rfkill", "block", "bluetooth"])
        #subprocess.Popen(["sudo", "systemctl", "stop", "ssh.service"])
    else:
        print("QUIT STANDBY")
        standby_status = False
        subprocess.Popen(["sudo", "rfkill", "unblock", "bluetooth"])
        subprocess.Popen(["systemctl", "--user", "start", "player.service"])
    '''
    subprocess.Popen(["sudo", "rfkill", "block", "wifi"])
    subprocess.Popen(["sudo", "rfkill", "block", "bluetooth"])
    subprocess.Popen(["sudo", "systemctl", "stop", "ssh.service"])
    '''

def pressed(channel):
    elapsed = 0
    pressed_time = time.time()
    while GPIO.input(button_1) == GPIO.HIGH:
        elapsed = time.time()-pressed_time
        if elapsed >= 5:
            standby()
            return
    return

GPIO.add_event_detect(button_1, GPIO.RISING, callback=pressed, bouncetime=200)


def main():
    try:
        while True:
            time.sleep(10)
            pass
    except KeyboardInterrupt:
        GPIO.cleanup()

main()
