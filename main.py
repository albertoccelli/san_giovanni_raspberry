import subprocess
import os

path = os.environ["SM_DIR"]
print(path)

while True:
    try:
        #  connect bluetooth device
        bt_connect = subprocess.Popen(["python", f"{path}/bt_device.py"])
        bt_connect.wait()
        #  start player service
        demo = subprocess.Popen(["python", f"{path}/sm_demo.py"])
        demo.wait()
    except KeyboardInterrupt:
        subprocess.Popen(["killall", "paplay"])
        break
