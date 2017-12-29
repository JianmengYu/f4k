import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import moviepy as mp
from moviepy.editor import *
import os

movie = 'Desktop/summary_10fffb019a161c150ea970907278e082#201005091640.avi'
imgdir = 'frames'

clip = VideoFileClip(movie)
clip.save_frame(imgdir, 0.1)

extract_frames(movie, times, imgdir)
