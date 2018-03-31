#!/usr/bin/python

import sys

floor = ""
machine = ""

memsize = dict()
with open("/afs/inf.ed.ac.uk/user/s14/s1413557/machines/check/mem/mem.out", 'r') as mem:
	for l in mem.readlines():
		l = l.strip().split()
		if l[0] == "Checking:":
			machine = l[1]
		if l[0] == "MemTotal:" and machine != "":
			if l[1][:2] == "16":
				memsize[machine] = 16
			if l[1][:1] == "8":
				memsize[machine] = 8
		else:
			if machine != "":
				memsize[machine] = "Unknown"

with open("/afs/inf.ed.ac.uk/user/s14/s1413557/machines/check/mem/machines", 'r') as mac:
	for l in mac.readlines():
		l = l.strip().split()
		try:
			if l[0] == "hide":
				floor = l[1]
			if l[14] == floor:
				fname = floor[3:]
				fname = fname[0] + fname[2:]
				mname = l[10]
				print("{0},{1},{2}".format(mname,fname,memsize[mname]))
				#if fname == "412":
				#	print("echo \"Checking: {0}\"".format(mname))
				#	print("ssh {0} \"cat /proc/meminfo | head -1\"".format(mname))
		except Exception:
			continue 
