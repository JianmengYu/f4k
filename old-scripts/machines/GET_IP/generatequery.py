#!/usr/bin/python

import sys
import numpy as np

for c in np.arange(5):
	for d in np.arange(255):
		print("nslookup 129.215.{0}.{1}".format(c,d))
