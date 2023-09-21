import subprocess
from get_sinks import getSinks, getPaths
import yaml
import time

jack_sink = getSinks()[0]


def set_spkr_volume_max():
    try:
        p = getPaths()[1]
        print(p)
        command = ["dbus-send", "--system", "--type=method_call", "--print-reply", "--dest=org.bluez",
                   "/org/bluez/hci0/dev_78_5E_A2_F9_A5_9A", "org.bluez.MediaControl1.VolumeUp"]
        for i in range(30):
            lower_volume = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = lower_volume.communicate()
            lower_volume.wait()
            print(stdout)
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
