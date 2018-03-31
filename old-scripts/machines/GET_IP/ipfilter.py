#!/usr/bin/python

import sys

for line in sys.stdin:
	line = line.strip()
	tokens = line.split()
	if len(tokens) > 3:
		if tokens[1] == "name":
			ipa, ipb, ipc, ipd, stuff = tokens[0].split(".",4)
			name, sbd, stuff = tokens[3].split(".",2)
			if sbd == "inf":
				print("{0}.{1}.{2}.{3}\t{4}".format(ipd,ipc,ipb,ipa,name))
			#else:
			#	print("{0}.{1}.{2}.{3}\t{4}".format(ipd,ipc,ipb,ipa,tokens[3]))
