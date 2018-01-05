#!/usr/bin/python

import os
import errno

dirf = "/afs/inf.ed.ac.uk/group/ug4-projects/s1413557/features/"

for i in range(256):
	char = hex(i)[2:]
	if len(char) == 1:
		char = "0" + char
	filename = dirf + char[0] + "/" + char + "/"
	try:
		os.makedirs(os.path.dirname(filename))
		print(filename)
	except Exception:
		print("{0} exists".format(filename))
