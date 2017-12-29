#!/usr/bin/python

import sys

for line in sys.stdin:
	
	if line[5] == 'f':
		print("{0}\t{1}".format(line[0:5],line[16:61]))
