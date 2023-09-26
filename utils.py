import subprocess
import yaml
import time
from datetime import datetime


def print_datetime(argument):
    print(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\t{argument}")


def set_spkr_volume_max():
    try:
        command = ["dbus-send", "--system", "--type=method_call", "--print-reply", "--dest=org.bluez",
                   "/org/bluez/hci0/dev_78_5E_A2_F9_A5_9A", "org.bluez.MediaControl1.VolumeUp"]
        for i in range(30):
            raise_volume = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            raise_volume.wait()
            # print(stdout)
            time.sleep(0.05)
    except Exception as e:
        print(e)


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
    s_player = subprocess.Popen(["systemctl", "--user", "stop", "player.service"])
    s_player.wait()


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
    check = subprocess.Popen(["systemctl", "--user", "is-active", "player.service"], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, text=True)
    stdout, stderr = check.communicate()
    if "active" in stdout:
        if "inactive" in stdout:
            return False
        else:
            return True
    else:
        print("Error")


def get_sinks():
    command = "pactl list sinks"

    output = subprocess.check_output(command, shell=True, text=True)
    output_lines = output.splitlines()

    names = []
    paths = []
    for line in output_lines:
        if "Name" in line:
            names.append(line.split(":")[-1].replace(" ", ""))
        if "bluez.path" in line:
            paths.append(line.split(":")[-1].replace('"', '').replace(' ', ''))
    return names

def get_volumes():
    command = "pactl list sinks"

    output = subprocess.check_output(command, shell=True, text=True)
    output_lines = output.splitlines()

    volumes = []
    for line in output_lines:
        if "Volume" in line:
            if "Base" not in line:
                print(line.split("%"))
    return volumes

def get_paths():
    command = "pactl list sinks"

    output = subprocess.check_output(command, shell=True, text=True)
    output_lines = output.splitlines()

    names = []
    paths = []
    for line in output_lines:
        if "Name" in line:
            names.append(line.split(":")[-1].replace(" ", ""))
        if ".path" in line:
            paths.append(line.split("=")[-1].replace('"', '').replace(' ', ''))
    return paths


jack_sink = get_sinks()[0]
