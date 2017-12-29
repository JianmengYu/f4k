#!/usr/bin/python

import sys

headc = 'frame_info_'
tailc = '.txt'

for line in sys.stdin:
	movid, __, __ = line.strip().split(",")
	f1 = movid[:1]
	f2 = movid[:2]
	path = '/run/media/s1413557/TOSHIBA\\ EXT/f4k_extracted_image/output/summaries/{0}/{01}/'.format(f1,f2) + headc + movid + tailc

	print("cat {0} | wc -l".format(path))
