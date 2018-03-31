#!/usr/bin/python

import sys
import socket

local = socket.gethostname().split(".")[0]
hosts = local
lastcheck = ""
count = 1

for line in sys.stdin:
	line = line.strip()
	line = line.split()
	
	if line[0] == "Checking:":

		if lastcheck != "":
			hosts += "," + line[1]
			count += 1
		if line[1] != local:
			lastcheck = line[1]

	else:
		
		lastcheck = ""

if lastcheck != "":
	hosts += "," + line[1]
	count += 1

print("echo \"{0}\"".format("Setting hosts..."))
print("HOSTS={0}".format(hosts))
print("export HOSTS")
print("echo \"{0}\"".format("Finished Setting hosts, echo \$HOSTS"))
print("echo $HOSTS")

print("echo \"{0}\"".format("Setting hosts' processor count..."))
print("HOSTSNUM={0}".format(count*4))
print("export HOSTSNUM")
print("echo \"{0}\"".format("Finished Setting hosts' processor count, echo \$HOSTSNUM"))
print("echo $HOSTSNUM")
