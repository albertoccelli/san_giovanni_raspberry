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
	from get_sinks import getSinks
	import os
	from player import Player

	# read audio files from folder
	script_dir = os.path.dirname(os.path.abspath(__file__))
	voice_path = f"{script_dir}/media/front/"
	bg_path = f"{script_dir}/media/neck/"
	voice_playlist = [f"{voice_path}{f}" for f in os.listdir(voice_path) if os.path.isfile(os.path.join(voice_path, f))]
	bg_playlist = [f"{bg_path}{f}" for f in os.listdir(bg_path) if os.path.isfile(os.path.join(bg_path, f))]

	print("Front playlist:")
	print(voice_playlist)
	print("Neck playlist: ")
	print(bg_playlist)

	# initiate players
	audio_sinks = getSinks()

	bluetooth = Player(audio_sinks[1])
	bluetooth.load(bg_playlist)
	bluetooth.play()
	jack = Player(audio_sinks[0])
	jack.load(bg_playlist)
	#jack.play()

	def btn_1_pressed(channel):
		print("Paused")
		if bluetooth.playing:
			bluetooth.pause()
		else:
			if bluetooth.stopped:
				bluetooth.play()
			else:
				bluetooth.resume()

	def rotation_1_callback(channel):
		if GPIO.input(DT_PIN) == GPIO.input(CLK_PIN):
			print("Next Track")
			bluetooth.next_track()
		else:
			print("Previous Track")
			bluetooth.prev_track()

	GPIO.add_event_detect(button_pin, GPIO.FALLING, callback=btn_1_pressed, bouncetime=200)
	GPIO.add_event_detect(DT_PIN, GPIO.BOTH, callback=rotation_1_callback, bouncetime=200)
	main()
