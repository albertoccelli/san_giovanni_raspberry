import subprocess

while True:
    try:
        #  connect bluetooth device
        bt_connect = subprocess.Popen(["python", "~/sm_demo/bt_device.py"])
        bt_connect.wait()
        #  start player service
        demo = subprocess.Popen(["python", "~/sm_demo/sm_demo.py"])
        demo.wait()
    except KeyboardInterrupt:
        subprocess.Popen(["killall", "paplay"])
        break
