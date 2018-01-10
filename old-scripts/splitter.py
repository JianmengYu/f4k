#!/usr/bin/python

import sys
import time

start = True
dirf = "/run/media/s1413557/TOSHIBA EXT/f4ktable/"
buffer_filename = []
buffer_string = []
index = -1
stime = time.time()

for line in sys.stdin:
	line = line.strip()
	#Empty line case
	if len(line) > 2:
		tokens = line.split(",")
		if len(tokens) < 9: #IGNORE BROKEN LINES
			continue
		if (tokens[0] == "") or (len(tokens[0]) > 11):
			continue
		if not (tokens[0][0].isdigit()):
			continue

		if (int(tokens[0]) % 1000) == 0:
			size = len(buffer_string)
			remainingseconds = ((time.time() - stime) / float(tokens[0])) * (1500000000-int(tokens[0]))
			hour = int(remainingseconds) / 3600
			minute = int(remainingseconds) / 60 - 60 * hour
			printline = "processing detection: " + tokens[0]
			printline += "\nBuffer length: " + str(size)
			printline += "\nProbably still need " + str(hour) + " hours, " + str(minute) + " minutes"
			print(printline)
			#Cleanup buffer.
			for i in range(0,size):
				fname = buffer_filename[i]
				dirname = dirf + fname[0:1] + "/" + fname[0:2] + "/" + fname + ".txt"
				f = open(dirname,'a+')
				f.write(buffer_string[i])
				f.close()			
			buffer_filename = []
			buffer_string = []
			filename = ""
			index = 0
				
		if (start): #Start line only
			filename = tokens[2][1:-1]
			index = 0
			buffer_filename.append(filename)
			buffer_string.append(line + "\n")
			start = False
		else:
			newfilename = tokens[2][1:-1]
			if (filename != newfilename):
				if newfilename in buffer_filename:
					index = buffer_filename.index(newfilename)
					buffer_string[index] += (line + "\n")
				else:
					index = len(buffer_filename) #THIS ONE LINE, THIS ONE LINE
					buffer_filename.append(newfilename)
					buffer_string.append(line + "\n")
				filename = newfilename
			else:
				buffer_string[index] += (line + "\n")

#Cleanup buffer.
size = len(buffer_string)
for i in range(0,size):
	fname = buffer_filename[i]
	dirname = dirf + fname[0:1] + "/" + fname[0:2] + "/" + fname + ".txt"
	f = open(dirname,'a+')
	f.write(buffer_string[i])
	f.close()			
			
