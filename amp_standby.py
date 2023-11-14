import RPi.GPIO as GPIO
import time

standby_pin = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(standby_pin, GPIO.OUT)


print("STANDBY ON")
GPIO.output(standby_pin, 0)

time.sleep(5)

print("STANDBY OFF")
GPIO.output(standby_pin, 1)
