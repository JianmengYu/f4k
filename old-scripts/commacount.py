#!/usr/bin/python


import sys

for l in sys.stdin:
	ls = l.split(",")
	print(len(ls))
