#!/usr/bin/python

import sys
import socket

local = socket.gethostname().split(".")[0]
hosts = []
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

if lastcheck != "":
	hosts.append(lastcheck)


print("HOSTS:")
print("{0}".format(",".join(hosts)))

print("number of HOSTS")
print("{0}".format(len(hosts)))
