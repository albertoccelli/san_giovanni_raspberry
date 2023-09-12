import RPi.GPIO as GPIO
import time

button_pin = 27
DT_PIN = 17
CLK_PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(CLK_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def main():
	try:
		while True :
			time.sleep(1)
	except KeyboardInterrupt:
		GPIO.cleanup()

if __name__ == "__main__":

	def btn_pressed(channel):
		print("Pressed")

	def rotation_callback(channel):
		if GPIO.input(DT_PIN) == GPIO.input(CLK_PIN):
			print("Rotazione oraria")
		else:
			print("Rotazione antioraria")

	GPIO.add_event_detect(button_pin, GPIO.FALLING, callback=btn_pressed, bouncetime=200)
	GPIO.add_event_detect(DT_PIN, GPIO.BOTH, callback=rotation_callback, bouncetime=200)
	main()
