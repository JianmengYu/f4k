#!/usr/bin/python

import sys
import time

start = True
dirf = "/run/media/s1413557/TOSHIBA EXT/dump/"
changetimes = 1
linechangeoccurs = False
linechangecount = 1
starttime = time.time()
filelist = []

for line in sys.stdin:
	line = line.strip()
	if len(line) > 2:
		tokens = line.split(",")
		if (int(tokens[0]) % 1000) == 0:
			interval = time.time()-starttime
			if (interval)>0.001:
				print("It tooks: " + str(interval) + " SECS!")
				print("Opened files: " + str(filelist))
				remaintimes = ((1500000000 - int(tokens[0]))/1000 * interval)
				print("Gonna take: " + str(remaintimes / 3600) + " hour to finish")
			starttime = time.time()
			print("processing detection: " + tokens[0])
			linechangeoccurs = False
			linechangecount = 1
			filelist = []
		if (start): #Start line only
			filename = tokens[2][1:3]
			dirname = dirf + tokens[2][1:3] + ".txt"
			f = open(dirname,'a+')
			f.write(line)
			f.write("\n")
			start = False
		else:
			if (filename != tokens[2][1:3]):
				#print ("FILE CHANGE time: " + str(changetimes))
				#if (linechangeoccurs):
					#print("opening file: " + tokens[2][1:3] + ".txt")
				if (linechangecount > 100):
					linechangeoccurs = True
				linechangecount += 1
				changetimes += 1 
				f.close() #Close the file only if data change
				filename = tokens[2][1:3]
				dirname = dirf + tokens[2][1:3] + ".txt"
				f = open(dirname,'a+')
				f.write(line)
				f.write("\n")
				if not (filename in filelist):
					filelist.append(filename)
			else:
				f.write(line)
				f.write("\n")
f.close()
			
