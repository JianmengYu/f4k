#!/usr/bin/python

import sys

linenum = 1
inserting = False

for line in sys.stdin:
	line = line.strip()
	if (len(line)>1):
		if (line[0]!="I"):
			if inserting:
				print("-------------------- INSERTING DATA ending @ line#" + str(linenum-1) + "--------------------")
				inserting = False
			print(line)
		else:
			if not inserting:
				print("-------------------- INSERTING DATA starting line#" + str(linenum) + "--------------------")
				print("-------------------- SAMPLE LINE: " + line[:1000])
				inserting = True
			if inserting & ((linenum % 100)==0):
				print("-------------------- INSERTING DATA continue line#" + str(linenum) + "--------------------")
	linenum += 1
