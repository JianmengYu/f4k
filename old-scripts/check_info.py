#!/usr/bin/python

import sys

path_video = '/afs/inf.ed.ac.uk/group/ug4-projects/s1413557/video_info.txt'
vidinfo = dict()
with open(path_video,'r') as fp:
    for i, line in enumerate(fp):
        line = line.strip().split(",")
        #line[2] = (line[2]=="1")
        vidinfo[line[0]] = (line[1],line[2])


for line in sys.stdin:
	line = line.strip()
	info = vidinfo[line]
	print("{0},{1},{2}".format(line,info[0],info[1]))
