import subprocess

def getSinks():
	command = "pactl list sinks"

	output = subprocess.check_output(command, shell=True, text = True)
	output_lines = output.splitlines()

	sink = 0
	names = []
	paths = []
	for l in output_lines:
		if "Name" in l:
			names.append(l.split(":")[-1].replace(" ",""))
		if "bluez.path" in l:
			paths.append(l.split(":")[-1].replace('"', '').replace(' ', ''))
	return(names)

def getPaths():
        command = "pactl list sinks"

        output = subprocess.check_output(command, shell=True, text = True)
        output_lines = output.splitlines()

        sink = 0
        names = []
        paths = []
        for l in output_lines:
                if "Name" in l:
                        names.append(l.split(":")[-1].replace(" ",""))
                if ".path" in l:
                        paths.append(l.split("=")[-1].replace('"', '').replace(' ', ''))
        return(paths)


if __name__ == "__main__":
	print(getSinks())
