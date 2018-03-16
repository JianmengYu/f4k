#!/usr/bin/python

import os
import errno

#dirf = "/afs/inf.ed.ac.uk/group/ug4-projects/s1413557/output-delme/"
#dirf = "/afs/inf.ed.ac.uk/group/ug4-projects/s1413557/CNNoutput/"
dirf = "/afs/inf.ed.ac.uk/group/project/F4KC/output/"


for i in range(256):
	char = hex(i)[2:]
	if len(char) == 1:
		char = "0" + char
	filename = dirf + char[0] + "/" + char + "/"
	os.makedirs(os.path.dirname(filename))
	print(filename)
