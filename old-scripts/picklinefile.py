#!/usr/bin/python

import sys

count = 1;
output = "/run/media/s1413557/TOSHIBA EXT/fish_detection_table.txt"
f = open(output,'a+')

#Take from line 107340 to 441537, end at 441538
for line in sys.stdin:
	if (count % 100) == 0:
			print("processing line: " + str(count))
	if (count == 441538):
		f.close()
		break
	if (count > 107339):
		f.write(line)
	count += 1
	
