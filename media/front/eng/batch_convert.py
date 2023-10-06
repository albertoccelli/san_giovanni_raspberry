import os
import subprocess

files = os.listdir()
mp3_files = []

for f in files:
	if ".mp3" in f:
		mp3_files.append(f)

print(f)

for file in mp3_files:
	filename = file.split(".")[0]
	print(filename)
	print(f"Converting {filename}")
	os.system(f"mpg123 -w {filename}.wav {filename}.mp3")

os.system("rm *.mp3")
