import RPi.GPIO as GPIO
import time

from config import *


def btn1_pressed(channel):
    time_pressed = time.time()
    while GPIO.input(button_1) == GPIO.HIGH:
        print(time.time()-time_pressed)
        time.sleep(0.1)
        pass
    if (time.time()-time_pressed) >= 0.05:
        print(f"BUTTON 1 RELEASED (time: {time.time()-time_pressed})")
    time.sleep(0.2)

def btn2_pressed(channel):
    time_pressed = time.time()
    while GPIO.input(button_2) == GPIO.HIGH:
        print(time.time()-time_pressed)
        time.sleep(0.1)
        pass
    if (time.time()-time_pressed) >= 0.05:
        print(f"BUTTON 2 RELEASED (time: {time.time()-time_pressed})")

def btn3_pressed(channel):
    print("BTN3 PRESSED")
    '''
    time_pressed = time.time()
    while GPIO.input(button_3) == GPIO.HIGH:
        time_pressed = time.time()
        print(time.time()-time_pressed)
        time.sleep(0.1)
        pass
    if (time.time()-time_pressed) >= 0.05:
        print(f"BUTTON 3 RELEASED (time: {time.time()-time_pressed})")
    '''
def btn4_pressed(channel):
    while GPIO.input(button_4) == GPIO.HIGH:
        pass
    print("BTN4 PRESSED")
    time.sleep(0.1)

def btn5_pressed(channel):
    while GPIO.input(button_5) == GPIO.HIGH:
        pass
    print("BTN5 PRESSED")
    time.sleep(0.1)

#GPIO.add_event_detect(button_1, GPIO.RISING, callback=btn1_pressed, bouncetime=150)
#GPIO.add_event_detect(button_2, GPIO.RISING, callback=btn2_pressed, bouncetime=150)
#GPIO.add_event_detect(button_3, GPIO.RISING, callback=btn3_pressed, bouncetime=150)
#GPIO.add_event_detect(button_4, GPIO.RISING, callback=btn4_pressed, bouncetime=200)
GPIO.add_event_detect(button_5, GPIO.RISING, callback=btn5_pressed, bouncetime=200)

def main():
    try:
        while True:
            time.sleep(0.02)
            print(GPIO.input(button_5))
            pass
    except KeyboardInterrupt:
        GPIO.cleanup()

main()
