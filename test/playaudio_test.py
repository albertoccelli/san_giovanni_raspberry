import pyaudio
import sounddevice as sd

file_audio = "usb/07_somayitsecretlybegin.wav"

def play_audio(file, output):
	p = pyaudio.PyAudio()
	audio_format = pyaudio.paInt16
	channels = 2
	rate = 44100

	stream = p.open(format=audio_format,
                    channels=channels,
                    rate=rate,
                    output=True,
                    output_device_index=output)

	with open(file, 'rb') as f:
		audio_data = f.read()
		stream.write(audio_data)

	stream.stop_stream()
	stream.close()

	p.terminate()

output_device_index = 1

play_audio(file_audio, output_device_index)
