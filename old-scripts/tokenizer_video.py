#!/usr/bin/python

import sys

for line in sys.stdin:
	line = line.strip()
	#line = line[39:-2] #For table 'connection_track'
	line = line[28:-2] #For table 'fish_detection'
	tokens = line.split("),(")
	for l in tokens:
		l = l.split(",")
		if len(l[0])==47:
			if l[5] == "240":
				big = 0
				#print("YEABOI")
			elif l[5] == "480":
				big = 1
				#print("YEEEEEABOI")
			else:				
				#print("NYET!BOI")
				continue
			print("{0},{1},{2}".format(l[0][1:-1], l[1], big))
