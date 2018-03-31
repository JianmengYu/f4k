#!/usr/bin/python

import sys
import numpy as np

for c in np.arange(2,4):
	for d in np.arange(255):
		print("echo \"Checking usage of: 129.215.{0}.{1}\"".format(c,d))
		print("ping 129.215.{0}.{1} -c 1 -i 0.2".format(c,d))
