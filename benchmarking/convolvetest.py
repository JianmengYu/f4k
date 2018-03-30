#!/afs/inf.ed.ac.uk/user/s14/s1413557/miniconda2/bin/python

from __future__ import print_function
import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
import sys
import cv2
import copy
import numpy as np
import pandas as pd
from scipy import signal, stats
from datetime import datetime
from scipy import ndimage as ndi
import tensorflow as tf
import matplotlib.pyplot as plt


def tfConvR(img,filters):
    flip = [slice(None, None, -1), slice(None, None, -1)]
    tfa = tf.reshape(np.array(filters,dtype=np.float32).astype(np.float32), [5, 5, 5, 1])
    tfa = tfa[flip]
    tfi = tf.reshape(np.array(img,dtype=np.float32), [len(img)/5, 100, 100, 5])
    tf.Session().run(tf.nn.conv2d(tfi,tfa,strides=[1,1,1,1],padding='SAME'))
    
multiplier = int(sys.argv[1])

filters = [None] * 5
for i in range(5):
    filters[i] = np.random.rand(5,5)*2-1
randImgs = [None] * 1000 * multiplier
for i in range(1000 * multiplier):
    randImgs[i] = np.random.rand(100,100)*256

time = datetime.now()
tfConvR(randImgs,filters)
cost = datetime.now() - time
print("TensorFlow.nn.conv2d   took total of {0}".format(cost))
