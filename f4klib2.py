#Misc code that is mostly not really usable.

import os
import sys
import cv2
import copy
import pymatlab
import numpy as np
import pandas as pd
import moviepy as mp
from moviepy.editor import *
from scipy import signal, stats
from bitarray import bitarray
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.image as mpimg
from matplotlib.path import Path
from bitarray import bitarray

from f4klib import *

def loadPickables(movs):
    pickables = []
    ids = []
    for i, item in enumerate(movs):
        if i == 1584:
            break
        date = item[0][-12:]
        if date[:8] == "20110422" or date[-4:] == "0800":
            pickables.append(item)
            ids.append(i)
    return (ids, pickables)

def printClassExamples():
    movs = loadMovids()
    samp_vids = [343 ,638,6,5,13 ,146,408,153,408,5  ]
    samp_fram = [1000,80 ,0,0,136,301,60 ,290,1  ,177]
    
    plt.subplots(2,5,figsize=(15,6))
    
    for i in range(10):
        plt.subplot(2,5,i+1)
        plt.xticks([])
        plt.yticks([])
        plt.xlabel("Class {0}".format(i+1))
        info, clip, hasContour, contour, fish_id, frames = loadVideo(movs[samp_vids[i]])
        plt.imshow(clip[samp_fram[i]])
        cline = contour[samp_fram[i]]
        thisContour = getContour(cline, return_what="Normalized")
        plt.scatter(thisContour[:,0],thisContour[:,1],s=1)
    plt.show()


def plotContourFromOriginalFile(path, limit_amount=400, add_milk=False):
    if limit_amount > 0:
        plt.subplots((limit_amount+19)/20,20,figsize=(15,0.75*((limit_amount+19)/20)))
    with open(path,'r') as fp:
        for i, line in enumerate(fp):
            line = line[37:-3].split("),(")
            counter = 0
            
            for l in line:
                
                if  counter >= limit_amount:
                    continue
                counter += 1
                
                try:
                    detid, fid, vid, what, date, rest = l.split(",",5)
                    binary, what1, what2, what3 = rest.rsplit(",",3)
                    a = bitarray()
                    string = binary[1:-1]
                    a.frombytes(string)
                    binary = cleanLine(a.to01())
                except ValueError:
                    continue
                
                plt.subplot((limit_amount+19)/20,20,counter)
                plotContour(binary,add_milk=add_milk)
    plt.show()
    
def plotContour(binary, add_milk=False):
    
    points2 = getContour(binary, return_what="Normalized")
    if add_milk:
        plt.imshow(getMask(points2))
    plt.scatter(points2[:,0],points2[:,1],s=1)
    plt.xticks([])
    plt.yticks([])
    plt.gca().invert_yaxis()
    
def plotContourOnImage(info, clip, hasContour, contour, picker, debug=False):
    det_id = int(info[picker,0])
    if hasContour[picker]:
        string2 = contour[picker]
        if debug:
            print("Printing detection_id: {0}".format(det_id))
        points2 = getContour(string2,debug=debug)

#         plt.subplots(1,1,figsize=(15,15))  
        plt.subplots(1,2,figsize=(15,10))  
        plt.subplot(121)
        plt.imshow(clip[picker]) 
        plt.xticks([])
        plt.yticks([])
        plt.subplot(122)
        plt.imshow(clip[picker])   
        plt.xticks([])
        plt.yticks([]) 
        plt.axvline(9,                linewidth=1, color='r', alpha=0.4)
        plt.axvline(10+info[picker,1],linewidth=1, color='r', alpha=0.4)
        plt.axhline(9,                linewidth=1, color='r', alpha=0.4)
        plt.axhline(10+info[picker,2],linewidth=1, color='r', alpha=0.4)
        plt.scatter(points2[:,0],points2[:,1],s=5)

        plt.show()
        
def plotStuff(info, clip, hasContour, contour, movid, limit_lower=0, limit_upper=20, width=5, gap=1, classify=False):
    
    if movid[2] == "1":
        frame_size = "640x480"
    else:
        frame_size = "320x240"
    
    frames = len(hasContour)
    if not(frames > limit_upper): #limit output
        limit_upper = frames

    show_axis = width <= 5
    depth = int(np.ceil((limit_upper-limit_lower)*1.0/width))
    
    f, ax = plt.subplots(depth,width,figsize=(20,20*depth/width))
    
    for i in np.arange(limit_lower, (limit_upper-limit_lower)*gap+limit_lower, gap):
        plt.subplot(depth,width,(i-limit_lower)/gap+1)
        plt.imshow(clip[i])
        plt.xticks([])
        plt.yticks([])

        if classify:
            if hasContour[i]:
                cline = contour[i]
                thisContour = getContour(cline, return_what="Normalized")
                plt.scatter(thisContour[:,0],thisContour[:,1],s=(3.0/width),color='red')
                result, delta, length = FEIF(cline,case=frame_size,return_info=True)
                #for print X and Y range
                contX, contY, contW, contH, firstXPoint, padding, binary2 = extractMeta(cline)
                plt.gca().add_patch(patches.Rectangle((9,9),info[i,1],info[i,2],fill=False,linewidth=1,color='red'))
                if result:
                    plt.gca().add_patch(patches.Rectangle((0,0),100,100,fill=False,linewidth=50.0/width,color='red'))
                else:
                    plt.gca().add_patch(patches.Rectangle((0,0),100,100,fill=False,linewidth=50.0/width,color='green'))
                if show_axis:
                    plt.gca().set_xlabel("{0},{1},{2},{3:.0f}%\nX:{4}-{5} Y:{6}-{7}"
                                     .format(info[i,0],length,delta,delta/(length*0.01),
                                            contX,contX+contW,contY,contY+contH))
            else:
                plt.gca().add_patch(patches.Rectangle((0,0),100,100,fill=False,linewidth=50.0/width,color='yellow'))
                if show_axis:
                    plt.gca().set_xlabel("{0},NO CONTOUR".format(info[i,0]))
        #else:
            #plt.gca().set_xlabel("{0},{1}".format(info[i,0],info[i,1:4]))
            #plt.gca().add_patch(patches.Rectangle((9,9),info[i,1],info[i,2],
            #                                      fill=False,linewidth=1,color='red'))
    plt.show()
    
def loadSqlOriginal(path):
    #VERY OLD DONT USE
    ids = []
    original = []
    binaries = []
    with open(path, 'r') as f:
        for i, line in enumerate(f):
            try:
                detid, fid, vid, what, date, rest = line.split(",",5)
                binary, what1, what2, what3 = rest.rsplit(",",3)
                string = binary[1:-1]
                a = bitarray()
                a.frombytes(string)
                ids.append(detid)
                original.append(string)
                binaries.append(a)
            except ValueError:
                ValueError.message
                continue
    return np.vstack((ids,original,binaries)).T

def seperate_fish(contour,w):
    mask = np.full((100,100), 0, dtype=np.uint8)
    cv2.fillPoly(mask, np.int32([contour]), (255,))
    moments = cv2.moments(mask)
    (x, y) = (int(moments['m10']/moments['m00']), int(moments['m01']/moments['m00']))
    
    hl = int(round(9+w*0.25))
    hr = int(round(9+w*0.75))
    
    full_fish = getMask(contour)
    head_fish = copy.deepcopy(full_fish)
    head_fish[:,:x]=False
    tail_fish = copy.deepcopy(full_fish)
    tail_fish[:,x:]=False
    top_fish = copy.deepcopy(full_fish)
    top_fish[y:,:]=False
    bot_fish = copy.deepcopy(full_fish)
    bot_fish[:y,:]=False
    hhead_fish = copy.deepcopy(full_fish)
    hhead_fish[:,:hr]=False
    htail_fish = copy.deepcopy(full_fish)
    htail_fish[:,hl:]=False
    
    return (full_fish,head_fish,tail_fish,top_fish,bot_fish,hhead_fish,htail_fish)

def normalizeRGB(image):
    weight = np.sum(image,axis=2,dtype = np.uint16)
    weight[weight < 1] = 1
    return image/(weight*1.0)[:,:,None]

def getMask(normilizedContourPoints):
    #VERY SLOW DONT USE
    p = Path(normilizedContourPoints)
    nx, ny = 100, 100
    x, y = np.meshgrid(np.arange(nx), np.arange(ny))
    x, y = x.flatten(), y.flatten()
    points = np.vstack((x,y)).T
    grid = p.contains_points(points)
    grid = grid.reshape((ny,nx))
    return grid

def showTransformedImage(picker, clip, hasContour, contour):
    if hasContour[picker]:
        image1 = clip[picker]
        thiscontour = getContour(contour[picker])
        mask = np.full(image1.shape, 0, dtype=np.uint8)
        cv2.fillPoly(mask, np.int32([thiscontour]), (255,)*3)
        image2 = cv2.cvtColor(image1,cv2.COLOR_RGB2YUV)
        image3 = normalizeRGB(image2)[:,:,0]
        image4 = cv2.bitwise_or(cv2.bitwise_not(mask),image1)
        image5 = cv2.cvtColor(image4,cv2.COLOR_RGB2YUV)
        image6 = normalizeRGB(image5)[:,:,0]
        image7 = cv2.bitwise_and(mask,image1)
        image8 = cv2.cvtColor(image7,cv2.COLOR_RGB2YUV)
        image9 = normalizeRGB(image8)[:,:,0]
        labels = ["RGB of N","YUV of N","Normalized Y of N",
                  "RGB of WC","YUV of WC","Normalized Y of WC",
                  "RGB of BC","YUV of BC","Normalized Y of BC"]
        plt.subplots(1,9,figsize=(18,2))
        for index, image in enumerate([image1,image2,image3,image4,image5,image6,image7,image8,image9]):
            plt.subplot(1,9,index+1)
            if (index+1)%3==0:
                plt.imshow(image, cmap='gray')
            else:
                plt.imshow(image)
            plt.xticks([])
            plt.yticks([])
            plt.xlabel(labels[index])
            
        plt.show()
    else:
        print("No contour for this image dummy.")
        
def printCNNweight():
    basepath = '/afs/inf.ed.ac.uk/user/s14/s1413557/f4k-2017-msc-master/matt-msc/src/lua/cnn/models/'
    if os.name=="nt":
        basepath =  'C:/Users/YuJianmeng/f4k/matt-msc/src/lua/cnn/models/'
    path_plasu = 'filters/B_C/1/'
    path_plasu2 = 'filters/N/1/'
    path_plasu3 = 'filters/W_C/1/'
    #img = cv2.imread(basepath+path_plasu+'1.png')
    plt.subplots(24,16,figsize=(10,10))
    for i in range(64):
        plt.subplot(24,16,i+1)
        img = cv2.imread(basepath+path_plasu+str(i+1)+'.png')
        plt.imshow(img)
        plt.xticks([])
        plt.yticks([])
    for i in range(64):
        plt.subplot(24,16,i+65)
        img = cv2.imread(basepath+path_plasu+str(i+1)+'.png')
        plt.imshow(normalizeRGB(img))
        plt.xticks([])
        plt.yticks([])
    for i in range(64):
        plt.subplot(24,16,i+129)
        img = cv2.imread(basepath+path_plasu2+str(i+1)+'.png')
        plt.imshow(img)
        plt.xticks([])
        plt.yticks([])
    for i in range(64):
        plt.subplot(24,16,i+193)
        img = cv2.imread(basepath+path_plasu2+str(i+1)+'.png')
        plt.imshow(normalizeRGB(img))
        plt.xticks([])
        plt.yticks([])
    for i in range(64):
        plt.subplot(24,16,i+257)
        img = cv2.imread(basepath+path_plasu3+str(i+1)+'.png')
        plt.imshow(img)
        plt.xticks([])
        plt.yticks([])
    for i in range(64):
        plt.subplot(24,16,i+321)
        img = cv2.imread(basepath+path_plasu3+str(i+1)+'.png')
        plt.imshow(normalizeRGB(img))
        plt.xticks([])
        plt.yticks([])
    plt.show()
    
def printSeperateFish(picker, picker2):
    movs = loadMovids()
    movid = movs[picker]
    info, clip, hasContour, contour, fish_id, frames = loadVideo(movid,print_info=False, print_image=False)
    cline = contour[picker2]
    thisContour = getContour(cline)

    full_fish, head_fish, tail_fish, top_fish, bot_fish, hhead_fish, htail_fish = seperate_fish(thisContour,info[picker2][1])
    image = clip[picker2]

    #Temp stuff
    hf = np.array((head_fish.astype(int)*255)[:,:,None], dtype=np.uint8)
    hf = np.dstack((hf,hf,hf))
    tf = np.array((tail_fish.astype(int)*255)[:,:,None], dtype=np.uint8)
    tf = np.dstack((tf,tf,tf))
    tpf = np.array((top_fish.astype(int)*255)[:,:,None], dtype=np.uint8)
    tpf = np.dstack((tpf,tpf,tpf))
    btf = np.array((bot_fish.astype(int)*255)[:,:,None], dtype=np.uint8)
    btf = np.dstack((btf,btf,btf))
    hhf = np.array((hhead_fish.astype(int)*255)[:,:,None], dtype=np.uint8)
    hhf = np.dstack((hhf,hhf,hhf))
    htf = np.array((htail_fish.astype(int)*255)[:,:,None], dtype=np.uint8)
    htf = np.dstack((htf,htf,htf))

    #White mask with black shape
    mask = np.full(image.shape, 255, dtype=np.uint8)
    roi_corners = np.int32([thisContour])
    ignore_mask_color = (0,)*3
    cv2.fillPoly(mask, roi_corners, ignore_mask_color)

    # apply the mask
    masked_image = cv2.bitwise_or(image, mask)

    #get values
    moments = cv2.moments(cv2.bitwise_not(mask)[:,:,0])
    xy = (int(moments['m10']/moments['m00']), int(moments['m01']/moments['m00']))

    plt.subplots(1,8,figsize=(20,5))
    plt.subplot(181)
    plt.imshow(image)
    plt.subplot(182)
    plt.imshow(masked_image)
    plt.gca().add_patch(patches.Circle(xy,1,fill=True,linewidth=5,color='red'))
    plt.subplot(183)
    plt.imshow(cv2.bitwise_or(image, cv2.bitwise_not(hf)))
    plt.subplot(184)
    plt.imshow(cv2.bitwise_or(image, cv2.bitwise_not(tf)))
    plt.subplot(185)
    plt.imshow(cv2.bitwise_or(image, cv2.bitwise_not(tpf)))
    plt.subplot(186)
    plt.imshow(cv2.bitwise_or(image, cv2.bitwise_not(btf)))
    plt.subplot(187)
    plt.imshow(cv2.bitwise_or(image, cv2.bitwise_not(hhf)))
    plt.subplot(188)
    plt.imshow(cv2.bitwise_or(image, cv2.bitwise_not(htf)))
    plt.show()
    
def histc(list1, bins):
    hist,__ = np.histogram(list1, bins)
    lastbin = np.sum(list1 == 1)
    hist[-1] = hist[-1] - lastbin
    hist = np.append(hist, lastbin)
    return hist

def generateFeatureVector(info, contour, hasContour, clip, picker):
    cline = contour[picker]
    thisContour = getContour(cline)
    full, head, tail, top, bottom, hhead, htail = seperate_fish(thisContour,info[picker][1])
    image = clip[picker]
    norm_image = normalizeRGB(image)
    h_image = cv2.cvtColor(image,cv2.COLOR_RGB2HSV)[:,:,0]/180.0
    
    bins = np.arange(0,1.02,0.02)
    histrange_nr = [0, 0.01742,0.125,0.1884,0.226,0.26,0.2934,0.328,0.372,0.4512, 1]
    histrange_ng = [0, 0.298,0.3276,0.35,0.3734,0.404,0.4334,0.466,0.505,0.59, 1]
    histrange_h = [0, 0.2246,0.291,0.463,0.5648,0.6034,0.6248,0.6422,0.675,0.7164, 1]
    
    # ===== Normalized Red =====
    
    tempimage = norm_image[:,:,0][head]
    f_0001_0051 = histc(tempimage, bins)
    tempimage = norm_image[:,:,0][tail]
    f_0052_0102 = histc(tempimage, bins)
    tempimage = norm_image[:,:,0][top]
    f_0103_0153 = histc(tempimage, bins)
    tempimage = norm_image[:,:,0][bottom]
    f_0154_0204 = histc(tempimage, bins)
    tempimage = norm_image[:,:,0][full]
    f_0205_0255 = histc(tempimage, bins)
    
    # ===== Normalized Green =====
    
    tempimage = norm_image[:,:,1][head]
    f_0256_0306 = histc(tempimage, bins)
    tempimage = norm_image[:,:,1][tail]
    f_0307_0357 = histc(tempimage, bins)
    tempimage = norm_image[:,:,1][top]
    f_0358_0408 = histc(tempimage, bins)
    tempimage = norm_image[:,:,1][bottom]
    f_0409_0459 = histc(tempimage, bins)
    tempimage = norm_image[:,:,1][full]
    f_0460_0510 = histc(tempimage, bins)
    
    # ===== Normalized Hue =====
    
    tempimage = h_image[head]
    f_0511_0561 = histc(tempimage, bins)
    tempimage = h_image[tail]
    f_0562_0612 = histc(tempimage, bins)
    tempimage = h_image[top]
    f_0613_0663 = histc(tempimage, bins)
    tempimage = h_image[bottom]
    f_0664_0714 = histc(tempimage, bins)
    tempimage = h_image[full]
    f_0715_0765 = histc(tempimage, bins)
    
    # ===== Normalized Red =====
    
    tempimage = norm_image[:,:,0][head]
    f_0766_0776 = histc(tempimage, histrange_nr)
    tempimage = norm_image[:,:,0][tail]
    f_0777_0787 = histc(tempimage, histrange_nr)
    tempimage = norm_image[:,:,0][top]
    f_0788_0798 = histc(tempimage, histrange_nr)
    tempimage = norm_image[:,:,0][bottom]
    f_0799_0809 = histc(tempimage, histrange_nr)
    tempimage = norm_image[:,:,0][full]
    f_0810_0820 = histc(tempimage, histrange_nr)
    
    # ===== Normalized Green =====
    
    tempimage = norm_image[:,:,1][head]
    f_0821_0831 = histc(tempimage, histrange_ng)
    tempimage = norm_image[:,:,1][tail]
    f_0832_0842 = histc(tempimage, histrange_ng)
    tempimage = norm_image[:,:,1][top]
    f_0843_0853 = histc(tempimage, histrange_ng)
    tempimage = norm_image[:,:,1][bottom]
    f_0854_0864 = histc(tempimage, histrange_ng)
    tempimage = norm_image[:,:,1][full]
    f_0865_0875 = histc(tempimage, histrange_ng)
    
    # ===== Normalized Hue =====
    
    tempimage = h_image[head]
    f_0876_0886 = histc(tempimage, histrange_h)
    tempimage = h_image[tail]
    f_0887_0897 = histc(tempimage, histrange_h)
    tempimage = h_image[top]
    f_0898_0908 = histc(tempimage, histrange_h)
    tempimage = h_image[bottom]
    f_0909_0919 = histc(tempimage, histrange_h)
    tempimage = h_image[full]
    f_0920_0930 = histc(tempimage, histrange_h)
    
def featureNames():
    feature_names =[]
    for i in np.arange(1,256):
        feature_names.append("Normalized Red {0}".format(i))
    for i in np.arange(1,256):
        feature_names.append("Normalized Green {0}".format(i))
    for i in np.arange(1,256):
        feature_names.append("Normalized H {0}".format(i))
    for i in np.arange(1,56):
        feature_names.append("Normalized Red (bin2) {0}".format(i))
    for i in np.arange(1,56):
        feature_names.append("Normalized Green (bin2) {0}".format(i))
    for i in np.arange(1,56):
        feature_names.append("Normalized H (bin2) {0}".format(i))
    feature_names.append("Curve Shape")
    feature_names.append("Curve Tail Ratio")
    for i in np.arange(1,13):
        feature_names.append("Fish density static {0}".format(i))
    for i in np.arange(1,11):
        for j in np.arange(1,73):
            feature_names.append("Co-occurance Matrix ({0},{1})".format(j,i))
    for i in np.arange(1,43):
        feature_names.append("Moment Invariant {0}".format(i))
    for i in np.arange(1,681):
        feature_names.append("PHOG {0}".format(i))
    for i in np.arange(1,16):
        feature_names.append("Fourier Descriptor {0}".format(i))
    for i in np.arange(1,161):
        feature_names.append("Gabor Filter (texture) {0}".format(i))
    for i in np.arange(1,64):
        feature_names.append("AMI features {0}".format(i))
    feature_names.append("Half Head Ratio")
    feature_names.append("Half Tail Ratio")
    feature_names.append("Animation Score")
    for i in np.arange(1,5):
        feature_names.append("Curvature {0}".format(i))
    for i in np.arange(1,5):
        feature_names.append("Erraticity {0}".format(i))
    for i in np.arange(1,21):
        feature_names.append("Gabor Filter (edge) {0}".format(i))
    return feature_names
    
def printCameras():
    # `camera_id` int(11) NOT NULL AUTO_INCREMENT,
    # `video_number` int(11) NOT NULL,
    # `location` varchar(100) NOT NULL DEFAULT '',
    # `camera_lens` varchar(60) DEFAULT NULL,
    # `camera_angle` smallint(6) DEFAULT NULL,
    # `depth` tinyint(3) DEFAULT NULL,

    path_camera = '/afs/inf.ed.ac.uk/group/ug4-projects/s1413557/cameras'
    if os.name == "nt":
        path_camera = 'E:/cameras'
    with open(path_camera,'r') as fp:
        for i, line in enumerate(fp):
            line = line[1:-2].split("),(")
            for l in line:
                print(l)
                l = l.split(",")
                #print()