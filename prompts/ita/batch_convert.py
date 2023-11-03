import os

mp3_files = []

f = os.listdir()

for i in f:
    if ".mp3" in i:
        mp3_files.append(i)

print(mp3_files)

for audio in mp3_files:
    wav_file = audio.split(".mp3")[0].replace(" ","").lower()
    command = f"mpg123 -w {wav_file}.wav {audio}"
    print(command)
    os.system(command)
