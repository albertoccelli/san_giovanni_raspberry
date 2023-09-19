import RPi.GPIO as GPIO
import time
import threading

TRIG_PIN = 23
ECHO_PIN = 24

treshold = 100

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

class DistanceSensor:
	def __init__(self, trigpin, echopin, on_posedge_callback = None, on_negedge_callback = None):
		self.trigpin = trigpin
		self.echopin = echopin
		self.on_posedge_callback = on_posedge_callback
		self.on_negedge_callback = on_negedge_callback
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(trigpin, GPIO.OUT)
		GPIO.setup(echopin, GPIO.IN)
		self.distance = None
		self.treshold = 50
		self.running = False
		self.lock = threading.Lock()

	def get_distance(self):
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
			if self.distance > self.treshold and p_distance < self.treshold:
				print("Posedge")
				if self.on_posedge_callback:
					self.on_posedge_callback()
			elif self.distance < self.treshold and p_distance > self.treshold:
				print("Negedge")
				if self.on_negedge_callback:
					self.on_negedge_callback()
			self.lock.release()
			p_distance = self.distance
			time.sleep(1)

	def start_measuring(self):
		if not self.running:
			self.running = True
			self.thread = threading.Thread(target = self.measure_distance)
			self.thread.daemon = True
			self.thread.start()

	def stop_measurement(self):
		if self.running:
			self.running = False
			self.thread.join()


if __name__ == "__main__":

	def custom_cb():
		print("OCHEI")

	sensor = DistanceSensor(TRIG_PIN, ECHO_PIN, on_posedge_callback = custom_cb, on_negedge_callback = custom_cb)

	try:
		sensor.start_measuring()
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		sensor.stop_measurement()
		GPIO.cleanup()
