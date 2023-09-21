import RPi.GPIO as GPIO
import time
import subprocess
from sensor import DistanceSensor
import threading

button_pin = 27
DT_PIN = 17
CLK_PIN = 18
ECHO_PIN = 24
TRIG_PIN = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(CLK_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

if __name__ == "__main__":
	from get_sinks import getSinks
	import os
	from player import Player
	from utils import load_config

	config_file = "/home/a.occelli/sm_demo/config.yaml"

	# read audio files from folder
	script_dir = os.path.dirname(os.path.abspath(__file__))
	voice_path = f"{script_dir}/media/front/"
	bg_path = f"{script_dir}/media/neck/"
	voice_playlist = [f"{voice_path}{f}" for f in os.listdir(voice_path) if os.path.isfile(os.path.join(voice_path, f))]
	bg_playlist = [f"{bg_path}{f}" for f in os.listdir(bg_path) if os.path.isfile(os.path.join(bg_path, f))]
	voice_playlist = bg_playlist

	# make sure that the paplay service is not suspended
	subprocess.Popen(["pactl", "suspend-sink", "0"])

	print("Front playlist:")
	print(voice_playlist)
	print("Neck playlist: ")
	print(bg_playlist)

	# initiate players
	# make sure that the bt device is ready to play:
	while True:
		print("Please wait...")
		audio_sinks = getSinks()
		if len(audio_sinks) == 2:
			break
		time.sleep(2)

	bluetooth = Player(audio_sinks[1])
	bluetooth.load(bg_playlist)
	bluetooth.play()
	jack = Player(audio_sinks[0])
	jack.load(voice_playlist)
	jack.play()

	def toggle_play_pause():
		if bluetooth.playing:
			print("Paused")
			bluetooth.pause()
			jack.pause()
		else:
			if bluetooth.stopped:
				bluetooth.play()
				jack.play()
			else:
				print("Resume")
				bluetooth.resume()
				jack.resume()

	def btn_1_pressed(channel):
		toggle_play_pause()

	def rotation_1_callback(channel):
		if GPIO.input(DT_PIN) == GPIO.input(CLK_PIN):
			print("Next Track")
			bluetooth.next_track()
			jack.next_track()
		else:
			print("Previous Track")
			bluetooth.prev_track()
			jack.prev_track()

	def distance_pause():
		print("User too far away: pause")
		bluetooth.pause()
		jack.pause()

	def distance_resume():
		print("User detected: resume")
		bluetooth.resume()
		jack.resume()

	# define sensors/button detect functions
	GPIO.add_event_detect(button_pin, GPIO.FALLING, callback=btn_1_pressed, bouncetime=200)
	GPIO.add_event_detect(DT_PIN, GPIO.BOTH, callback=rotation_1_callback, bouncetime=200)
	d_sensor_enabled = load_config(config_file).get("distance_sensor_enabled")
	print(f"Sensor status: {d_sensor_enabled}")
	if d_sensor_enabled == True:
		print("Sensor started")
		d_sensor = DistanceSensor(TRIG_PIN, ECHO_PIN, on_posedge_callback = distance_pause, on_negedge_callback = distance_resume)
		d_sensor.treshold = load_config(config_file).get("treshold")
		d_sensor.start_measuring()
	# the main function
	def main():
		try:
			while True:
				time.sleep(1)
		except KeyboardInterrupt:
			subprocess.Popen(["pactl", "suspend-sink", "0"])
			subprocess.Popen(["killall", "paplay"])
			GPIO.cleanup()
	main()
