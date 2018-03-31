#!/usr/bin/python

import sys
import socket

local = socket.gethostname().split(".")[0]
hosts = []
needrestart = []
lastcheck = ""
hosts.append(local)

for line in sys.stdin:
	line = line.strip()
	
	if line == "":
		continue

	line = line.split()
	
	if line[0] == "Checking:":

		if lastcheck != "":
			hosts.append(lastcheck)
		if line[1] != local:
			lastcheck = line[1]

	else:

		if line[0] == "shell-init:" and lastcheck != "":
			needrestart.append(lastcheck)
		
		lastcheck = ""


if lastcheck != "":
	hosts.append(lastcheck)

with open("/afs/inf.ed.ac.uk/user/s14/s1413557/machines/needrestart.txt","w") as f:
	for una in needrestart:
		f.write(una)
		f.write("\n")

print("HOSTS:")
print("{0}".format(",".join(hosts)))

print("number of HOSTS")
print("{0}".format(len(hosts)))
