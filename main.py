import subprocess
import os

cwd = os.getcwd()

print(cwd)
while True:
    try:
        #  connect bluetooth device
        bt_connect = subprocess.Popen(["python", "bt_device.py"])
        bt_connect.wait()
        #  start player service
        demo = subprocess.Popen(["python", "sm_demo.py"])
        demo.wait()
    except KeyboardInterrupt:
        subprocess.Popen(["killall", "paplay"])
        break
