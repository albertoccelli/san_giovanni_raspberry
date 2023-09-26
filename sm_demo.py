import RPi.GPIO as GPIO
import time
import subprocess
from sensor import DistanceSensor
from utils import print_datetime

button_pin = 27
dt_pin = 17
clk_pin = 18
echo_pin = 24
trig_pin = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dt_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(clk_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

if __name__ == "__main__":
	from utils import getSinks
	import os
	from player import Player
	from utils import load_config, set_spkr_volume_max

	# configuration file
	config_file = "/home/a.occelli/sm_demo/config.yaml"
	d_sensor_enabled = load_config(config_file).get("distance_sensor_enabled")	# load distance sensor configuration
	button_pin = load_config(config_file).get("button_pin")				# pause/play button 
	button_pin = load_config(config_file).get("button_pin")  # pause/play button

	# read audio files from folder
	script_dir = os.path.dirname(os.path.abspath(__file__))
	voice_path = f"{script_dir}/media/front/"
	bg_path = f"{script_dir}/media/neck/"
	voice_playlist = [f"{voice_path}{f}" for f in os.listdir(voice_path) if os.path.isfile(os.path.join(voice_path, f))]
	bg_playlist = [f"{bg_path}{f}" for f in os.listdir(bg_path) if os.path.isfile(os.path.join(bg_path, f))]
	voice_playlist = bg_playlist

	# make sure that the paplay service is not suspended
	subprocess.Popen(["pactl", "suspend-sink", "0"])

	print_datetime("Front playlist:")
	print_datetime(voice_playlist)
	print_datetime("Neck playlist: ")
	print_datetime(bg_playlist)

	# initiate players
	# make sure that the bt device is ready to play:
	while True:
		print_datetime("Please wait...")
		audio_sinks = getSinks()
		if len(audio_sinks) == 2:
			break
		time.sleep(1)

	# Set volume of neckband to max
	print_datetime("Setting neckband to max")
	set_spkr_volume_max()
	print_datetime("Done")

	bluetooth = Player(audio_sinks[1])
	bluetooth.load(bg_playlist)
	bluetooth.play()
	jack = Player(audio_sinks[0])
	jack.load(voice_playlist)
	jack.play()

	def toggle_play_pause():
		if bluetooth.playing:
			print_datetime("Paused")
			bluetooth.pause()
			jack.pause()
		else:
			if bluetooth.stopped:
				bluetooth.play()
				jack.play()
			else:
				print_datetime("Resume")
				bluetooth.resume()
				jack.resume()

	def btn_1_pressed(channel):
		toggle_play_pause()

	def rotation_1_callback(channel):
		if GPIO.input(dt_pin) == GPIO.input(clk_pin):
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
	GPIO.add_event_detect(dt_pin, GPIO.BOTH, callback=rotation_1_callback, bouncetime=200)
	print(f"Sensor status: {d_sensor_enabled}")
	if d_sensor_enabled == True:
		print("Sensor started")
		d_sensor = DistanceSensor(trig_pin, echo_pin, on_posedge_callback = distance_pause, on_negedge_callback = distance_resume)
		d_sensor.treshold = load_config(config_file).get("treshold")
		d_sensor.start_measuring()

	# the main function
	def main():
		try:
			while True:
				# check if bluetooth device is available
				print(getSinks())
				if len(getSinks())<2:
					print("Fatal: lost connection")
					subprocess.Popen(["pactl", "suspend-sink", "0"])
					bluetooth.stop()
					jack.stop()
					return
				time.sleep(1)

		except KeyboardInterrupt:
			subprocess.Popen(["pactl", "suspend-sink", "0"])
			subprocess.Popen(["killall", "paplay"])
			GPIO.cleanup()

	main()
