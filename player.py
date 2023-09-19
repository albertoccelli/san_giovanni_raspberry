import subprocess
import psutil
import time
import threading
import signal
import RPi.GPIO as GPIO


button_pin = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

class Player:

	def __init__(self, sink):
		print(f"Loading player - {sink}")
		self.sink = sink
		self.audio_process = None
		self.current_index = 0
		self.playlist = None
		self.current_track = None
		self.playing = False
		self.stopped = True

	def load(self, playlist):
		self.playlist = playlist
		self.current_track = self.playlist[self.current_index]
		return self.playlist

	def play_audio(self, filename = None):
		self.playing = True
		self.stopped = False
		self.current_track = self.playlist[self.current_index]
		if filename == None:
			filename = self.current_track
		while self.playing:
			try:
				print(f"Playing {filename} on {self.sink}")
				self.audio_process=subprocess.Popen(["paplay", f"--device={self.sink}", filename], stdout = subprocess.PIPE, stderr = subprocess.PIPE, text = True)
				stdout, stderr = self.audio_process.communicate()
				if stderr:
					print(f"Error reproducing audio: {stderr}")
					break
				self.audio_process.wait()
			except Exception as e:
				print(f"Error riproducing audio: {e}")
				break

	def play(self):
		self.audio_thread = threading.Thread(target=self.play_audio)
		self.audio_thread.daemon = True
		self.audio_thread.start()

	def pause(self):
		self.playing = False
		print(f"Pause {self.sink}")
		#self.audio_process.send_signal(subprocess.signal.SIGSTOP)
		pause = subprocess.Popen(["pactl", "suspend-sink", self.sink, "1"])
		pause.wait()

	def resume(self):
		self.playing = True
		print(f"Resume {self.sink}")
		#self.audio_process.send_signal(subprocess.signal.SIGCONT)
		resume = subprocess.Popen(["pactl", "suspend-sink", self.sink, "0"])
		resume.wait()

	def stop(self):
		try:
			self.playing = False
			self.stopped = True
			self.audio_process.terminate()
			self.audio_thread.join()
			print(f"Stop {self.sink}")
		except Exception as e:
			if "nonetype" in str(e).lower():
				print("No audio to stop")

	def next_track(self):
		self.stop()
		self.current_index += 1
		if self.current_index >= len(self.playlist):
			self.current_index = 0
		self.current_track = self.playlist[self.current_index]
		print(f"{self.sink}: Next track -> {self.current_track}")
		self.play()

	def prev_track(self):
		self.stop()
		self.current_index -=1
		if self.current_index < 0:
			self.current_index = len(self.playlist)-1
		self.current_track = self.playlist[self.current_index]
		print(f"{self.sink}: Previous track <- {self.current_track}")
		self.play()

def main():
	try:
		while True :
			time.sleep(1)
	except KeyboardInterrupt:
		GPIO.cleanup()


if __name__ == "__main__":

	from get_sinks import getSinks
	import os

	# read audio files from folder
	script_dir = os.path.dirname(os.path.abspath(__file__))
	voice_path = f"{script_dir}/media/front/"
	bg_path = f"{script_dir}/media/neck/"
	voice_playlist = [f"{voice_path}{f}" for f in os.listdir(voice_path) if os.path.isfile(os.path.join(voice_path, f))]
	print(voice_playlist)
	bg_playlist = [f"{bg_path}{f}" for f in os.listdir(bg_path) if os.path.isfile(os.path.join(bg_path, f))]

	# get sink information
	while True:
		try:
			bt_sink = getSinks()[1]
			jack_sink = getSinks()[0]
			break
		except Exception as e:
			pass
		time.sleep(3)

	# initialize players
	bluetooth = Player(bt_sink)
	jack = Player(jack_sink)
	# initialize GPIOs
	def bt_next(channel):
		bluetooth.next_track()
	def bt_toggle_pause(channel):
		if bluetooth.playing:
			bluetooth.pause()
		else:
			bluetooth.resume()
	GPIO.add_event_detect(button_pin, GPIO.FALLING, callback=bt_next, bouncetime=200)
	#GPIO.add_event_detect(button_pin, GPIO.FALLING, callback=bt_toggle_pause, bouncetime=200)

	# setup player
	bluetooth.load(bg_playlist)
	bluetooth.play()
	jack.load(voice_playlist)
	jack.play()
	print(voice_playlist)
	# main loop function
	main()
