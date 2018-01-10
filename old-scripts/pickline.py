#!/usr/bin/python

import sys

count = 1;

for line in sys.stdin:
	if (count == 441538):
		break
	if (count >= 107340):
		print(line)
	count += 1
