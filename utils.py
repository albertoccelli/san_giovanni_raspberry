import subprocess
from get_sinks import getSinks
import yaml

jack_sink = getSinks()[0]

def load_config(file):
	with open(file, "r") as stream:
		try:
			configuration = yaml.safe_load(stream)
			return configuration
		except yaml.YAMLError as e:
			print(f"Error: {e}")
			return None

def stop_player():
	# stop player.service
	stop_player = subprocess.Popen(["systemctl", "--user", "stop", "player.service"])
	stop_player.wait()


def audio_prompt(filename):
	# play prompt
	subprocess.Popen(["pactl", "suspend-sink", "0"])
	play_prompt = subprocess.Popen(["paplay", f"--device={jack_sink}", filename])
	play_prompt.wait()

def start_player():
	# restart player.service
	subprocess.Popen(["pactl", "suspend-sink", "0"])
	restart_player = subprocess.Popen(["systemctl", "--user", "start", "player.service"])
	restart_player.wait()

def check_player():
	# check if player is running
	check = subprocess.Popen(["systemctl", "--user", "is-active", "player.service"], stdout = subprocess.PIPE, stderr = subprocess.PIPE, text = True)
	stdout, stderr = check.communicate()
	if "active" in stdout:
		if "inactive" in stdout:
			return False
		else:
			return True
	else:
		print("Error")
