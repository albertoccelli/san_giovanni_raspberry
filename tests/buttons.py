from config import *
import time



def button1_pressed(channel):
    print("BUTTON 1 PRESSED")

def button2_pressed(channel):
    print("BUTTON 2 PRESSED")

def button3_pressed(channel):
    print("BUTTON 3 PRESSED")

def button4_pressed(channel):
    print("BUTTON 4 PRESSED")

def button5_pressed(channel):
    print("BUTTON 5 PRESSED")


GPIO.add_event_detect(button_1, GPIO.RISING, callback=button1_pressed, bouncetime=200)
GPIO.add_event_detect(button_2, GPIO.RISING, callback=button2_pressed, bouncetime=200)
GPIO.add_event_detect(button_3, GPIO.RISING, callback=button3_pressed, bouncetime=200)
GPIO.add_event_detect(button_4, GPIO.RISING, callback=button4_pressed, bouncetime=200)
GPIO.add_event_detect(button_5, GPIO.RISING, callback=button5_pressed, bouncetime=200)


def main():
    try:
        while True:
            time.sleep(10)
            pass
    except KeyboardInterrupt:
        GPIO.cleanup()

main()
