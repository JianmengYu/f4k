#!/usr/bin/python

import sys

count = 1;
output = "/run/media/s1413557/TOSHIBA EXT/video_table.txt"
f = open(output,'a+')
start = False

#Take from line 482873 to 482982, end at 482983
for line in sys.stdin:
	if (count % 100) == 0:
			print("processing line: " + str(count))
	if (count == 482873):
		start = True
	if start:
		if count == 482983:
			f.close()
			break
		f.write(line)
	count += 1
	
