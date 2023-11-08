import RPi.GPIO as GPIO
import time
import numpy as np

GPIO.setmode(GPIO.BCM)

DATA_PIN = 19
GPIO.setup(DATA_PIN, GPIO.IN)

data = []
n_averages = 10000
sample_rate = 10000
try:
    while True:
        data_state = GPIO.input(DATA_PIN)
        if data_state == GPIO.LOW:
            data.append(1)
        else:
            data.append(0)
        time.sleep(1/sample_rate)
        if len(data) >= sample_rate:
            data = data[-sample_rate:]
        while True:
            if int(time.time()) % 1 == 0:
                print(np.average(data))
                break

except KeyboardInterrupt:
    pass

# Pulisci i pin GPIO prima di uscire
GPIO.cleanup()
