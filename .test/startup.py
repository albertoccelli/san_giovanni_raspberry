import subprocess
import time
from get_sinks import getSinks

print("Welcome to San Marco Demo")
time.sleep(1)

check_pa = subprocess.Popen(["pulseaudio", "--check"], stderr = subprocess.PIPE, stdout = subprocess.PIPE, text = True)
stdout, stderr = check_pa.communicate()
if stderr:
	print(stderr)
try:
    enable_pulseaudio = subprocess.Popen(["pulseaudio", "--start"])
except subprocess.CalledProcessError as e:
    print(f"Errore durante l'avvio di PulseAudio: {e}")
enable_pulseaudio.wait()

device = getSinks()[0]
audio = subprocess.Popen(["paplay", f"--device={device}", "/home/a.occelli/sm_demo/prompts/welcome.wav"])
audio.wait(1)
