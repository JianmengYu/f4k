#!/usr/bin/python

import sys

for line in sys.stdin:
	
	line = line.strip()
	line = line.split()

	print("wc -l /run/media/s1413557/TOSHIBA\ EXT/f4k_extracted_image/output/summaries/{0}frame_info_{1}.txt".format(line[0],line[1]))
