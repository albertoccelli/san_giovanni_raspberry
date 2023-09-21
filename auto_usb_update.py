import pyudev
import time
import subprocess
import os
from utils import getSinks

controlfile = ".update_smdemo.txt"
jack_sink = getSinks()[0]


def stop_player():
	# stop player.service
	stopplayer = subprocess.Popen(["systemctl", "--user", "stop", "player.service"])
	stopplayer.wait()
	return


def audio_prompt(filename):
	# play prompt
	play_prompt = subprocess.Popen(["paplay", f"--device={jack_sink}", filename])
	play_prompt.wait()


def start_player():
	# restart player.service
	restart_player = subprocess.Popen(["systemctl", "--user", "start", "player.service"])
	restart_player.wait()


def get_usb_path():
	path = None
	disk = subprocess.check_output(["lsblk", "-p"]).decode("utf-8")
	disk = disk.split("\n")
	for d in disk:
		d = d.split(" ")
		while True:
			try:
				d.remove("")
			except ValueError:
				break
		if len(d) > 1 and d[2] == "1":  # check if removable
			if "part" in d[5]:  # check if it's a partition
				path_found = True
				path = d[0].split("─")[-1]
	return path

def wait_for_usb():
	path = ""
	path_found = False
	while not path_found:
		disk = subprocess.check_output(["lsblk", "-p"]).decode("utf-8")
		disk = disk.split("\n")
		for d in disk:
			d = d.split(" ")
			while True:
				try:
					d.remove("")
				except ValueError:
					break
			if len(d) > 1 and d[2] == "1":  # check if removable
				if "part" in d[5]:  # check if it's a partition
					path_found = True
					path = d[0].split("─")[-1]
	return path


def mount_usb(usb_path, mount_path):
	print(f"Mounting usb on {mount_path}")
	# create mount point
	create_mp = subprocess.Popen(["sudo", "mkdir", mount_path])
	create_mp.wait()
	# mount usb drive
	mount = subprocess.Popen(["sudo", "mount", usb_path, mount_path])
	mount.wait()
	print("Successfully mounted")


def usb_in_callback(event):
	if event.device_node is not None and event.action == "add":
		print(f"USB detected:")
		# get path of the usb
		path = wait_for_usb()
		print(path)
		s_path = path
		m_path = "/media/usb-drive"
		t_path = "/home/a.occelli/sm_demo"
		# mount the usb into the s_path folder
		mount_usb(s_path, m_path)
		update(m_path, t_path)
		stop_player()
		return


def update(source, target):
	stop_player()
	# check if there is the source folder
	check = subprocess.Popen(["ls", "-a", f"{source}/sm_copy"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
							 text=True)
	stdout, stderr = check.communicate()
	if stderr:
		# Case of error
		print("ERROR:")
		print(stderr)
		audio_prompt("/home/a.occelli/sm_demo/prompts/usb_error.wav")
		start_player()
		return
	check = stdout.split("\n")
	print(check)
	time.sleep(1)
	# check if usb drive is allowed to update
	if controlfile in check:
		# create backup in the root folder and usb
		audio_prompt("/home/a.occelli/sm_demo/prompts/wait_update.wav")
		# copy config file
		print("Copying configuration files")
		copy_config = f"cp -r {source}/sm_copy/*.yaml {target}"
		os.system(copy_config)
		# copy audio files for the neckband
		print("Copying neck audio file")
		neck_files = subprocess.check_output(["ls", f"{source}/sm_copy/"])
		print(neck_files)
		command = f"cp -r {source}/sm_copy/media/neck/*.wav {target}/media/neck/"
		os.system(command)

		# end update
		print("Copy successful")
		audio_prompt("/home/a.occelli/sm_demo/prompts/update_complete.wav")
		start_player()
	else:
		audio_prompt("/home/a.occelli/sm_demo/prompts/usb_error.wav")
		print("Not allowed to copy from this usb")
	time.sleep(1)
	start_player()
	return


context = pyudev.Context()

monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by(subsystem='usb')

observer = pyudev.MonitorObserver(monitor, callback=usb_in_callback)
observer.start()

try:
	observer.join()
except KeyboardInterrupt:
	observer.stop()
	observer.join()
