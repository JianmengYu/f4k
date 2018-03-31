#!/usr/bin/python

import sys

hosts = []
unavailable = []
#count = 1
prevname = ""

for line in sys.stdin:
	line = line.strip()
	if line == "":
		continue
	line = line.split()
	if line[0] == "---":
		prevname = line[1].split('.')[0]
	if prevname != "" and len(line)>8:
		if line[7] == "100%":
			unavailable.append(prevname)

	if line[-1] == "ms":
		if line[0] == "64":
			name = line[3].split('.')[0]
			hosts.append(name)
			#count += 1

with open("/afs/inf.ed.ac.uk/user/s14/s1413557/machines/unavailable.txt","w") as f:
	for una in unavailable:
		f.write(una)
		f.write("\n")

#Print a .sh script to check map
for h in hosts:
	print("echo \"{0} {1}\"".format("Checking:",h))
	print("ssh {0} who".format(h))
	#print("ping {0} -c 1".format(h))
