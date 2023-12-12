from utils import curwd
import os

home = os.environ["HOME"]
service_dir = f"{home}/.config/systemd/user/"

def service_create(name, description, service, install):
    text = description+service+install
    with open(f"{service_dir}{name}.service", "w") as f:
        f.write(text)
    os.system(f"systemctl --user enable {name}.service")

# main service
description = "[Unit]\nDescription=The main demo routine. Handles standby function\n\n"
service = f"[Service]\nExecStart=python {curwd}/main.py\nEnvironment=SM_DIR={curwd}\n\n"
install = f"[Install]\nWantedBy=default.target"

service_create("main_demo", description, service, install)

# player service
description = "[Unit]\nDescription=The main player service. Reproduces music via jack and bluetooth simultaneously.\n\n"
service = f"[Service]\nExecStart=python {curwd}/sm_demo.py\nEnvironment=SM_DIR={curwd}\n\n"
install = f"[Install]\nWantedBy=default.target"

service_create("player", description, service, install)

# sw update service
description = "[Unit]\nDescription=The update service. Waits for USB to be connected in order to perform update\n\n"
service = f"[Service]\nExecStart=python {curwd}/auto_usb_update.py\nEnvironment=SM_DIR={curwd}\n\n"
install = f"[Install]\nWantedBy=default.target"

service_create("sw_update", description, service, install)

# player service
description = "[Unit]\nDescription=Ensures stability to the system once turned on\n\n"
service = f"[Service]\nExecStart=python {curwd}/watchdog.py\nEnvironment=SM_DIR={curwd}\n\n"
install = f"[Install]\nWantedBy=default.target"

service_create("watchdog", description, service, install)

os.system("systemctl --user daemon-reload")
