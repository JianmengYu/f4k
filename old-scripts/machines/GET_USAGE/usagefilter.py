#!/usr/bin/python

import sys

ip = ""
reachable = False
user = ""

for line in sys.stdin:
	line = line.strip()
	tokens = line.split()
	if len(tokens) > 2:
		if tokens[0] == "Checking":
			if (ip != tokens[3]) & (ip != ""):
				if reachable:
					if user == "":
						print("IP: " + ip + " is free!")
					else:
						print("IP: " + ip + " is not free, used by " + user + "...")
				else:
					print("IP: " + ip + " unreachable!")
			ip = tokens[3]
			reachable = False
			user = ""
		if tokens[0] == "From": #From ip... Host Unreachable
			reachable = False
		if (tokens[0] == "64") & (tokens[1] == "bytes"): #Get echo
			reachable = True
		if reachable & (tokens[1] == ":0"):
			user = tokens[0]
