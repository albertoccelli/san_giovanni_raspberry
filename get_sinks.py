import subprocess

def getSinks():
	command = "pactl list sinks"

	output = subprocess.check_output(command, shell=True, text = True)
	output_lines = output.splitlines()

	sink = 0
	names = []

	for l in output_lines:
		if "Name" in l:
			names.append(l.split(":")[-1].replace(" ",""))
	return(names)


if __name__ == "__main__":
	print(getSinks())
