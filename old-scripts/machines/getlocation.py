#!/usr/bin/python

import sys

dic = dict()
with open("/afs/inf.ed.ac.uk/user/s14/s1413557/machines/check/ips.csv","r") as f:
	lines = f.readlines()
	for line in lines:
		line = line.strip()
		name, loc, mem = line.split(",",2)
		dic[name] = loc

for line in sys.stdin:
	line = line.strip()
	if line != "":
		print("Machine {0} at location {1}".format(line,dic[line]))

