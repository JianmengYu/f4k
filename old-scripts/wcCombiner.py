#!/usr/bin/python

import sys

sum = 0

for line in sys.stdin:
	
	line = line.strip()
	sum += int(line.split()[0])

print("Total lines: {0}".format(sum))
