#!/usr/bin/python

import sys

summu = 0

for l in sys.stdin:
	summu += int(l.strip().split()[0])
print(summu)
