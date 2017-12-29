#!/usr/bin/python

import os
import errno

dirf = "/run/media/s1413557/TOSHIBA EXT/f4ktable/"

for i in range(256):
	char = hex(i)[2:]
	if len(char) == 1:
		char = "0" + char
	filename = dirf + char[0] + "/" + char + "/"
	os.makedirs(os.path.dirname(filename))
	print(filename)
