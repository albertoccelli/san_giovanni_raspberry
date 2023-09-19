import pyudev
import time
import subprocess
import os
from get_sinks import getSinks

controlfile = ".update_smdemo.txt"
jack_sink = getSinks()[0]

def stop_player():
	# stop player.service
	stop_player = subprocess.Popen(["systemctl", "--user", "stop", "player.service"])
	stop_player.wait()


def audio_prompt(filename):
	# play prompt
	play_prompt = subprocess.Popen(["paplay", f"--device={jack_sink}", filename])
	play_prompt.wait()

def start_player():
	# restart player.service
	restart_player = subprocess.Popen(["systemctl", "--user", "start", "player.service"])
	restart_player.wait()


def get_usb_path():
	path_found = False
	while path_found == False:
		disk = subprocess.check_output(["lsblk", "-p"]).decode("utf-8")
		disk = disk.split("\n")
		for d in disk:
			d = d.split(" ")
			while True:
				try:
					d.remove("")
				except ValueError:
					break
			if len(d) > 1 and d[2] == "1":	# check if removable
				if "part" in d[5]: 	# check if it's a partition
					path_found = True
					path = d[0].split("─")[-1]
	return path

def mount_usb(usb_path, mount_path):
	# create mount point
	create_mp = subprocess.Popen(["sudo", "mkdir", mount_path])
	create_mp.wait()
	# mount usb drive
	mount = subprocess.Popen(["sudo", "mount", usb_path, mount_path])
	mount.wait()


def usb_in_callback(event):
	if event.device_node != None and event.action == "add":
		print(f"USB detected:")
		path = get_usb_path()
		print(path)
		s_path = path
		m_path = "/media/usb-drive"
		t_path = "/home/a.occelli/sm_demo"
		print(f"Mounting usb on {m_path}")
		mount_usb(s_path, m_path)
		print("Successfully mounted")
		stop_player()
		check = subprocess.Popen(["ls", "-a", f"{m_path}/sm_copy"], stdout = subprocess.PIPE, stderr = subprocess.PIPE, text = True)
		stdout, stderr = check.communicate()
		if stderr:
			print("ERROR:")
			print(stderr)
			audio_prompt("/home/a.occelli/sm_demo/prompts/usb_error.wav")
			start_player()
			return
		check = stdout.split("\n")
		print(check)
		time.sleep(1)
		if controlfile in check:	# check if usb drive is good for update
			# copy from usb drive to folder
			audio_prompt("/home/a.occelli/sm_demo/prompts/wait_update.wav")
			# if found, copy config.yaml file into sm_demo folder
			copy_config = f"cp -r {m_path}/sm_copy/*.yaml {t_path}"
			os.system(copy_config)
			command = f"cp -r {m_path}/sm_copy/* {t_path}/usb"
			os.system(command)
			print("Copy successful")
			audio_prompt("/home/a.occelli/sm_demo/prompts/update_complete.wav")
			start_player()
		else:
			audio_prompt("/home/a.occelli/sm_demo/prompts/usb_error.wav")
			print("Not allowed to copy from this usb")
		time.sleep(1)
		start_player()
		return

def backup(target):
	print("Backup started")
	make_zip = subprocess.Popen(["zip", "-ru", target, "/home/a.occelli/sm_demo/"], stdout = subprocess.PIPE, stderr = subprocess.PIPE, text = True)
	while True:
		line = make_zip.stdout.readline()
		if not line: break
	make_zip.wait()
	if stderr:
                print("ERROR:")
                print(stderr)
	print(stdout)
	print("Backup complete")


def update(source, target):
	stop_player()
	# check if there is the source folder
	check = subprocess.Popen(["ls", "-a", f"{source}/sm_copy"], stdout = subprocess.PIPE, stderr = subprocess.PIPE, text = True)
	stdout, stderr = check.communicate()
	if stderr:
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
		copy_config = f"cp -r {m_path}/sm_copy/*.yaml {t_path}"
		os.system(copy_config)
		

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
