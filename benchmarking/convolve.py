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

def ndiConv(img,filters):
    for i in range(len(img)):
        for j in range(len(filters)):
            stuff = ndi.convolve(randImgs[i], filters[j], mode='constant', cval=0.0,  output=np.float64)
    return stuff

def sigConv(img,filters):
    for i in range(len(img)):
        for j in range(len(filters)):
            stuff = np.rot90(signal.convolve2d(np.rot90(randImgs[i], 2),np.rot90(filters[j],2),mode='same'),2)
    return stuff

def sfftConv(img,filters):
    bh, bw = filters[0].shape
    bh += -1
    bw += -1
    br = bw // 2
    bl = bw - br
    bb = bh // 2
    bt = bh - bb
    for i in range(len(img)):
        for j in range(len(filters)):
            stuff = signal.fftconvolve(randImgs[i],filters[j], mode='full')[bt:-bb,bl:-br]
    return stuff

def tfConvR(img,filters):
    flip = [slice(None, None, -1), slice(None, None, -1)]
    tfa = tf.reshape(np.array(filters,dtype=np.float32).astype(np.float32), [5, 5, 5, 1])
    tfa = tfa[flip]
    tfi = tf.reshape(np.array(img,dtype=np.float32), [len(img)/5, 100, 100, 5])
    tf.Session().run(tf.nn.conv2d(tfi,tfa,strides=[1,1,1,1],padding='SAME'))
    
filters = [None] * 5
for i in range(5):
    filters[i] = np.random.rand(5,5)*2-1
randImgs = [None] * 1000
for i in range(1000):
    randImgs[i] = np.random.rand(100,100)*256

time = datetime.now()
ndiConv(randImgs,filters)
cost = datetime.now() - time
print("Scipy.NDImage.convolve took total of {0}".format(cost))

time = datetime.now()
sigConv(randImgs,filters)
cost = datetime.now() - time
print("Signal.convolve2d      took total of {0}".format(cost))

time = datetime.now()
sfftConv(randImgs,filters)
cost = datetime.now() - time
print("Signal.fftconvolve     took total of {0}".format(cost))

time = datetime.now()
tfConvR(randImgs,filters)
cost = datetime.now() - time
print("TensorFlow.nn.conv2d   took total of {0}".format(cost))