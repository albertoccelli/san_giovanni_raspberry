import subprocess
from get_sinks import getSinks
import time
import utils

device = "Pixel"

def detect_disconnection():
	while True:
		if len(getSinks()) == 1:
			stop_player = subprocess.Popen(["systemctl", "--user", "stop", "player.service"])
			stop_player.wait()
			# lost connection with bluetooth device. Try again
			print("Lost connection with bluetooth device...")
			utils.audio_prompt("prompts/lost_connection.wav")
			try_reconnect = subprocess.Popen(["python", "/home/a.occelli/sm_demo/bt_device.py", device])
			try_reconnect.wait()
		elif len(getSinks()) == 2:
			# check if service is already active. Otherwise, activate it
			if utils.check_player() == False:
				print("Device found! Starting player")
				start_player = subprocess.Popen(["systemctl", "--user", "start", "player.service"])
				start_player.wait()
		time.sleep(2) # read change every second


if __name__ == "__main__":
	# as a first action, starts the player service
	utils.start_player()
	# run loop function detecting disconnections
	detect_disconnection()
