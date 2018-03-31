#!/usr/bin/python

import sys
import socket

local = socket.gethostname().split(".")[0]
hosts = local
count = 1

for line in sys.stdin:
	line = line.strip()
	
	name, loc, mem = line.split(",",2)
	#if loc=="606" or loc=="505" or loc=="508" or loc =="504":
	if (loc[0] == "3" or loc[0] == "4" or loc[0] == "7") and mem == "16":
		if name != local:
			hosts += "," + name
			count += 1

#Get all the names, and print count (77 in total)
#print(hosts)
#print(count)

#Print a .sh script to check map
for h in hosts.split(","):
	#print("echo \"{0} {1}\"".format("Checking:",h))
	#print("ssh {0} who".format(h))
	print("ping {0} -c 1".format(h))
