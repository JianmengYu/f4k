#!/usr/bin/python

import sys

for line in sys.stdin:
	line = line.strip()
	#line = line[39:-2] #For table 'connection_track'
	line = line[37:-2] #For table 'fish_detection'
	tokens = line.split("),(")
	for token in tokens:
		print token 
