from __future__ import print_function

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
from scipy import ndimage as ndi

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.image as mpimg
from matplotlib.path import Path
from bitarray import bitarray

from sklearn.decomposition import PCA
import pickle

### ===================================================== Util ===================================================== ###

def cleanLine(a):
    # Input:  corrupt 01 string
    # Return: cleaned  01 string
    length = len(a)//8
    binary = ""
    i = 0
    while i < length:
        byto16 = a[i*8:(i*8)+16]
        if byto16 == "0101110000110000":   # \0 -> null
            binary += "00000000"
            i+= 2
        elif byto16 == "0101110001011010": # \Z -> \x1a ???
            binary += "00011010"
            i+= 2
        elif byto16 == "0101110001101110": # \n -> \x0a
            binary += "00001010"
            i+= 2
        elif byto16 == "0101110001110010": # \r -> \x20
            binary +=  "00100000"
            i+= 2
        elif byto16 == "0101110000100010": # \" -> "
            binary += "00100010"
            i+= 2
        elif byto16 == "0101110000100111": # \' -> '
            binary += "00100111"
            i+= 2
        elif byto16 == "0101110001011100": # \\ -> \
            binary += "01011100"
            i+= 2
        else:
            binary += a[i*8:(i+1)*8]
            i+= 1
    return binary

def extractMeta(string, print_values=False):
    # Took a binary string of bb_cc, extract metadata from it.
    # 11:11:10:10:11:3:string
    # X :Y :W :H :x1:P:contour
    
    if len(string) < 56:
        raise Exception('Sutrin Not Rong Enafu')
    contX = int(string[0:11],2)
    contY = int(string[11:22],2)
    contH = int(string[22:32],2)
    contW = int(string[32:42],2)
    firstXPoint = int(string[42:53],2)
    padding = int(string[53:56],2)
    string2 = string[56:]
    
    if print_values:
        print("contX       Binary Value: {0}  Interpreted Value: {1}".format(string[0:11],contX))
        print("contY       Binary Value: {0}  Interpreted Value: {1}".format(string[11:22],contY))
        print("contH       Binary Value: {0}   Interpreted Value: {1}".format(string[22:32],contH))
        print("contW       Binary Value: {0}   Interpreted Value: {1}".format(string[32:42],contW))
        print("firstXPoint Binary Value: {0}  Interpreted Value: {1}".format(string[42:53],firstXPoint))
        print("padding     Binary Value: {0}          Interpreted Value: {1}".format(string[53:56],padding))
        print("Chaincode   Binary Value: \n{0}".format(string2))
    
    return (contX, contY, contW, contH, firstXPoint, padding, string2)

def movePoint(point, num):
    pointnew = point[:]
    if num == 0:
        pointnew[0] += 1
    if num == 1:
        pointnew[0] += 1
        pointnew[1] += 1
    if num == 2:
        pointnew[1] += 1
    if num == 3:
        pointnew[0] += -1
        pointnew[1] += 1
    if num == 4:
        pointnew[0] += -1
    if num == 5:
        pointnew[0] += -1
        pointnew[1] += -1
    if num == 6:
        pointnew[1] += -1
    if num == 7:
        pointnew[0] += 1
        pointnew[1] += -1
    return pointnew

def getContour(string, return_what="Normalized", debug=False):
    
    contX, contY, contW, contH, firstXPoint, padding, binary2 = extractMeta(string,print_values=debug)
    
    point = [firstXPoint,contY]
    points = []
    points.append(point)
    
    lmx = firstXPoint #left most X, to fix bug and stuff
    
    for i in range((len(binary2)-padding)/3):
        num = int(binary2[i*3:(i+1)*3],2)    
        pointnew = movePoint(point, num)
        points.append(pointnew)
        point = pointnew
        if point[0]<lmx:
            lmx = point[0]
            
    if point != points[0]:
        points.append(points[0])
        
    points = np.array(points)
    points2 = points - [lmx, contY] +10
    points3 = points - [lmx-contX,0]
    #points2 = [(elem1-int(lmx)+10, elem2-int(contY)+10) for elem1, elem2 in points]
    #points3 = [(elem1-lmx+contX, elem2) for elem1, elem2 in points]
    
    if return_what == "Both":
        return (points2, points3)
    if return_what == "Original":
        return points3
    return points2

### ===================================================== Classify/Extract ===================================================== ###

def earlyRemoval(movid, length):    
    video_id = movid[0]
    camera_id = int(movid[1])
    year = int(video_id[33:37])
    month = int(video_id[37:39])
    day = int(video_id[39:41])
    hour = int(video_id[41:43])
    
    #Remove lanyu night videos
    if camera_id == 44 or camera_id == 46:
        #print("LANYU SCUM!")
        if hour >= 18 or hour <= 6:
            #print("Wai so dim")
            return True
        
    #Skip videos that could give DICE too much pressure.
    #Usually having a dynamic background.
    if length >= 40000:
        return True
        
    #Videos that are too long for all kinds of issues
    if camera_id == 42 and year == 2012 and month >= 6 and month <= 8 and length >= 30000:
        #print("Buggish videos")
        return True
        
    if camera_id == 38 and year == 2010 and month == 1 and length >= 30000:
        #print("Early 2010 HDTV stuff")
        return True
    
    return False
    

def FEIF(string, case="320x240", return_info=False, matt_mode=True):
    
    if case == "320x240":
    #case 320x240
    # top 0 right 314 bottom 239 left 5 tsbottom 15 tsright 162
    # +1 for soft boundary
        top = 0
        right = 313
        bottom = 238
        left = 6
        tsright = 163
        tsbottom = 16 
    else:
    #case 640x480
    # top 0 right 633 bottom 479 left 5 tsbottom 32 tsright 265
        top = 0
        right = 632
        bottom = 478
        left = 6
        tsright = 266
        tsbottom = 33
        
    
    #My new criteria: 40 touching points or more than 20% touching
    limit1 = 30
    limit2 = 20 #%
    
    points2, points3 = getContour(string, return_what="Both")
    length = len(points2)
    
    if matt_mode:
        x2 = points2[:,0]
        y2 = points2[:,1]
        delta = np.sum(x2 == 100) + np.sum(y2 == 100)
        
        if delta < 10:
            x3 = points3[:,0]
            y3 = points3[:,1]
            delta += np.sum(x3<=left)+np.sum(x3>=right)+np.sum(y3<=top)+np.sum(y3>=bottom)
            if delta < limit1:
                delta += np.sum(np.logical_and(y3<=tsbottom,x3<=tsright))
                reject = delta >= limit1 or (delta*100/length) > limit2
            else:
                reject = True
        else:
            reject = True
            
        if return_info:
            return (reject,delta,length)
        else:
            return reject
    
    delta = 0
    reject = False
    
   #===========================================================  
    for x, y in points2:
        if x == 100 or y == 100:
            delta += 1
    if delta >= 10:
        reject = True
   #===========================================================  
    if not reject:
        for x, y in points3:
            if x <= left or x >= right or y<=top or y >= bottom or (x <= tsright and y <= tsbottom):
                delta += 1
    if delta >= 25:
        reject = True
   #===========================================================  
    if return_info:
        return (reject,delta,length)
    else:
        return reject
    
def getMattFeatures(info, clip, hasContour, contour, fish_id, print_info=False, ret_normalized_erraticity=False):
    
    time = datetime.now()
    counter = 0
    
    npfish = np.array(fish_id)
    det_id = info[:,0]
    length = len(hasContour)
    fishs = np.unique(npfish[hasContour])
    
    S = 10;
    W = 4
    G = signal.gaussian(2*W+1, std=1)
    G = G / np.sum(G)
    
    #Initialize gabor filters so we don't need to calculate it everytime.
    #Copy implement of Ahmad because sk-image and opencv's gabor work differently
    scales = np.repeat(np.arange(1.75,3,0.25),2)
    thetas = np.tile(np.array([0,90]),5)
    sigma_x = scales / np.pi * np.sqrt(np.log(2)/2) * 3 #(2^bandwidth+1)/(2^bandwidth-1); bdw=1;
    sigma_y = sigma_x/ 0.5 #gamma
    f = 1.0 / scales
    x0 = np.ceil(np.abs(sigma_x))
    y0 = np.ceil(np.abs(sigma_y))
    G_realz = [None]*10
    G_imagz = [None]*10
    for i in range(10):
        y, x = np.mgrid[-y0[i]:y0[i] + 1, -x0[i]:x0[i] + 1]
        rotx = x * np.cos(thetas[i]) + y * np.sin(thetas[i])
        roty = -x * np.sin(thetas[i]) + y * np.cos(thetas[i])
        g = np.zeros(y.shape, dtype=np.complex)
        g[:] = np.exp(-0.5 * (rotx ** 2 / sigma_x[i] ** 2 + roty ** 2 / sigma_y[i] ** 2))
        g *= np.exp(1j * (2 * np.pi * f[i] * rotx))
        g = g.T
        wNorm = np.sqrt(np.sum(np.real(g)**2+np.imag(g)**2))
        G_realz[i] = np.real(g) / wNorm
        G_imagz[i] = np.imag(g) / wNorm

    
    #Set outputs
    animation_scores = np.zeros(length)
    #Reduce these stuff to single array
    contour_size = np.zeros(length)
    contour_skewness = np.zeros(length)
    contour_kurtosis = np.zeros(length)
    contour_sum = np.zeros(length)
    erraticity_size = np.zeros(length)
    erraticity_skewness = np.zeros(length)
    erraticity_kurtosis = np.zeros(length)
    erraticity_sum = np.zeros(length)
    
    if ret_normalized_erraticity:
        norm_erraticity_size = np.zeros(length)
        norm_erraticity_skewness = np.zeros(length)
        norm_erraticity_kurtosis = np.zeros(length)
        norm_erraticity_sum = np.zeros(length)
        
    gabor_feature_mean = np.zeros((length,10))
    gabor_feature_std = np.zeros((length,10))
    
    for fish in fishs:
        mask = np.logical_and(npfish == fish,hasContour)
        index = np.arange(length)[mask]
        track = det_id[mask]
        tracklen = len(index)
        #It's always sorted?
        #print("")
        #print("Checking stuff: {0}".format(track))
        
        #Animation Score
        if tracklen == 1:
            animation_score = 0
            #print("AS: {0}".format(animation_score))
        else:
            #Why don't we use linspace?
            if tracklen < 5:
                target = np.arange(tracklen-1)
            else:
                target = np.floor(np.arange(0.0, tracklen-2, tracklen * 0.25)).astype(int)
            if target[-1] != (tracklen - 2):
                target = np.append(target,tracklen - 2)
            
            scores = np.zeros(len(target))
            
            for i, t in enumerate(target):
                N = info[index[t],1]
                M = info[index[t],2]
                Z = 1 / (1.0 * M * N)
                sub_f_t = clip[index[t]][S:M+S, S:N+S, :].astype(int)
                sub_f_tp1 = clip[index[t+1]][S:M+S, S:N+S, :].astype(int)
                scores[i] =  np.linalg.norm(np.sum(sub_f_t-sub_f_tp1,2,dtype=int)) * Z

            animation_score = np.average(scores)
                
            #print("AS: {0}".format(animation_score))
        for i in index:
            animation_scores[i] = animation_score
            
        #Contour Stuff
        K = np.zeros(tracklen)
        for i in np.arange(tracklen):
            c = getContour(contour[index[i]])
            X = c[:,0]
            Y = c[:,1]
            X1 = np.hstack((X[-W:],X,X[:W]))
            Y1 = np.hstack((Y[-W:],Y,Y[:W]))
            XX = np.convolve(X1,G,'same')
            YY = np.convolve(Y1,G,'same')
            Xu = np.gradient(XX)
            Yu = np.gradient(YY)
            Xuu = np.gradient(Xu)
            Yuu = np.gradient(Yu)
            k = ((Xu*Yuu-Xuu*Yu)/((Xu**2+Yu**2)**1.5))[W:-W]
            L2 = len(k)
            NFFT = 1<<(len(k)-1).bit_length()
            FT = np.fft.fft(k, NFFT) / L2
            f = L2 / 2*np.linspace(0, 1, NFFT/2 + 1)
            Yfreq = 2*np.abs(FT[0:NFFT/2+1])
            lag = 10
            if len(Yfreq) < lag:
                lag = 1
            #No moving average?
            y_avg = np.convolve(Yfreq, np.ones(lag)/float(lag), 'same')[lag-1:]
            scaled = np.convolve(np.add.reduceat(y_avg, np.arange(0, len(y_avg), 4)),[1,1],'valid')
            
            csize = len(scaled)
            cskew = stats.skew(scaled)
            ckurt = stats.kurtosis(scaled)
            csum = np.sum(scaled)
            
            contour_size[index[i]] = csize
            contour_skewness[index[i]] = cskew
            contour_kurtosis[index[i]] = ckurt
            contour_sum[index[i]] = csum
            
        #Erraticity
            t = np.array([csize, cskew, ckurt, csum])
            erraticity_score = np.zeros(4)
            if i != 0:
                erraticity_score += (t-tm1)**2
            tm1 = copy.deepcopy(t)
            
        if ret_normalized_erraticity:
            norm_erraticity_score = erraticity_score/float(tracklen)
            
        for i in np.arange(tracklen):
            
            erraticity_size[index[i]] = erraticity_score[0]
            erraticity_skewness[index[i]] = erraticity_score[1]
            erraticity_kurtosis[index[i]] = erraticity_score[2]
            erraticity_sum[index[i]] = erraticity_score[3]
            
            if ret_normalized_erraticity:
                norm_erraticity_size[index[i]] = norm_erraticity_score[0]
                norm_erraticity_skewness[index[i]] = norm_erraticity_score[1]
                norm_erraticity_kurtosis[index[i]] = norm_erraticity_score[2]
                norm_erraticity_sum[index[i]] = norm_erraticity_score[3]
            
        #Gabor Edge
        
        for i in np.arange(tracklen):
            thiscontour = getContour(contour[index[i]])
            I = np.full((100,100), 0, dtype=np.uint8)
            cv2.fillPoly(I, np.int32([thiscontour]), (255,))
            for j in range(10):
                #Slow!
                #Imgabout = np.rot90(signal.convolve2d(np.rot90(I, 2), np.rot90(G_imagz[j], 2), mode='same'),2)
                #Regabout = np.rot90(signal.convolve2d(np.rot90(I, 2), np.rot90(G_realz[j], 2), mode='same'),2)
                #Damn float64/16s
                Imgabout = ndi.convolve(I, G_realz[j], mode='constant', cval=0.0,  output=np.float64)
                Regabout = ndi.convolve(I, G_imagz[j], mode='constant', cval=0.0,  output=np.float64)
                gabout = np.sqrt(Imgabout**2+Regabout**2)
                targs = gabout[I>=1]
                targs[targs<0] = 0
                targs[targs>255] = 255
                targs = targs.astype(np.uint8)
                gabor_histo = np.histogram(targs,np.arange(0,257))[0] #np.histogram things
                gab_mean = np.dot(np.arange(0,256),gabor_histo) / sum(gabor_histo)
                gabor_feature_mean[index[i],j] = gab_mean
                gabor_feature_std[index[i],j] = np.dot((np.arange(0,256)-gab_mean)**2,gabor_histo) / sum(gabor_histo)
            
                
            counter += 1
            if print_info:
                print("Feature {1} took total of {0}".format(datetime.now() - time, counter) , end ='\r')
                
    if print_info:
        print("Calculate {1} feature took total of {0}".format(datetime.now() - time, counter))
        print("{0} out of {1} feature not calculated".format(length-counter, length))

    
    if ret_normalized_erraticity:
        output = np.column_stack((animation_scores,
                              contour_size,
                              contour_skewness,
                              contour_kurtosis,
                              contour_sum,
                              erraticity_size,
                              erraticity_skewness,
                              erraticity_kurtosis,
                              erraticity_sum,
                              norm_erraticity_size,
                              norm_erraticity_skewness,
                              norm_erraticity_kurtosis,
                              norm_erraticity_sum,
                              gabor_feature_mean,
                              gabor_feature_std))
    else:
        output = np.column_stack((animation_scores,
                              contour_size,
                              contour_skewness,
                              contour_kurtosis,
                              contour_sum,
                              erraticity_size,
                              erraticity_skewness,
                              erraticity_kurtosis,
                              erraticity_sum,
                              gabor_feature_mean,
                              gabor_feature_std))
    
    return output

### ===================================================== Loading data ===================================================== ###

def loadRange():
    path = "/afs/inf.ed.ac.uk/group/ug4-projects/s1413557/norm_const.npy"
    if os.path.isfile(path):
        ranges = np.load(path)
    else:
        features = loadSampleFeatures()        
        maxs = np.amax(features,0)
        mins = np.amin(features,0)
        fivep = (maxs-mins)/20
        maxs += -fivep
        mins += fivep
        ranges = np.vstack((mins,maxs))
        del features
        np.save(path,ranges)
    return ranges
        
def loadPCA(ranges):
    path = '/afs/inf.ed.ac.uk/group/ug4-projects/s1413557/pcaObject'
    if os.path.isfile(path):
        pca = pickle.load(open(path, 'rb'))
    else:
        features = loadSampleFeatures()
        normPhi = normalizePhi(features,ranges)
        pca = PCA().fit(normPhi)
        pickle.dump(pca, open(path, 'wb'))
        del features
        del normPhi
    return pca

def normalizePhi(features, constants):
    maxs = constants[1,:]
    mins = constants[0,:]
    features2 = (features*1.0-mins)/(maxs-mins)
    features2[np.isnan(features2)] = 0
    features2[features2<0] = 0
    features2[features2>1] = 1
    return features2

def loadSampleFeatures():
    movs = loadMovids()
    movs_length = loadLengths()
    features = np.array([],dtype="float64").reshape(0,2655)
    
    start = 30598
    end = 30695
    
    for i in np.arange(start,end):
        if movs_length[i] != 0:
            idee = movs[i][0]
            savepath = "/afs/inf.ed.ac.uk/group/ug4-projects/s1413557/features_sample/{0}/{1}/{2}".format(idee[0],idee[0:2],idee)
            f4kfeature = np.load(savepath+".f4kfeature.npy")
            mattfeature = np.load(savepath+".mattfeature.npy")
            feifmask = np.load(savepath+".feif.npy")
            comb = np.column_stack((f4kfeature, mattfeature[feifmask]))
            features = np.vstack((features,comb))
    return features

def loadTrainDataSet():
    movs = loadMovids()
    movs_length = loadLengths()
    idl = np.hstack((np.arange(30598,30633),np.arange(30634,30638)))
    location = "/afs/inf.ed.ac.uk/group/ug4-projects/s1413557/training/features/"
    start = True
    for i in idl:
        idee = movs[i][0]
        pca_feature = np.load(location+idee+".pcaFeature.npy")
        try:
            gts = loadGT(idee, movs_length[i], partial=True)
        except:
            gts = loadGT(idee, movs_length[i], partial=False)
        if start:
            features = pca_feature
            targets = gts
            start = False
        features = np.vstack((features,pca_feature))
        targets = np.hstack((targets,gts))
    mask = targets != 0
    features = features[mask]
    targets = targets[mask]
    return (features,targets)

def loadGT(video_id, length, partial=False):
    path = "/afs/inf.ed.ac.uk/group/ug4-projects/s1413557/training/targets/"+video_id+".f4kgt"
    if partial: path+=".partial"
    with open(path) as f:
        line = f.readlines()
        line = line[0][1:-1]
        tags = line.split(",")
        gts = [None] * length
        for t in tags:
            try:
                left, right = t.split(":",1)
                left = int(left.strip()[1:-1])-1
                right = int(right.strip())
                if right == 0:right=10
                gts[left] = right
            except Exception as e:
                print(t)
                print(e)
    gts = np.array(gts)
    gts[gts == None] = 0
    return gts

def loadMovids():
    path = '/afs/inf.ed.ac.uk/group/ug4-projects/s1413557/movie_ids_info.txt'
    if os.name == "nt":
        path = 'E:/movie_ids_info.txt'
    with open(path) as f:
        movs = f.readlines()
    return np.array([x.strip().split(",") for x in movs])

def loadLengths():
    path = '/afs/inf.ed.ac.uk/group/ug4-projects/s1413557/vidLen.txt'
    with open(path) as f:
        movs = f.readlines()
    return np.array([int(x.strip()) for x in movs])

def loadSql(path, frame_info, returnDict=False):
    
    sqlDict = dict()
    with open(path, 'r') as f:
        for i, line in enumerate(f):
            try:
                detid, fid, vid, what, date, rest = line.split(",",5)
                binary, what1, what2, what3 = rest.rsplit(",",3)
                string = binary[1:-1]
                a = bitarray()
                a.frombytes(string)
                sqlDict[int(detid)] = (a,fid)
            except ValueError:
                ValueError.message
                continue
                
       
    length = len(frame_info[:,0])
    mask = [False] * length
    sql = [-1] * length
    fid = [-1] * length
    for index, detid in enumerate(frame_info[:,0]):
        try:
            #sql[index] = sqlDict[int(detid)][0]
            sql[index] = cleanLine(sqlDict[int(detid)][0].to01())
            fid[index] = sqlDict[int(detid)][1]
            mask[index] = True
        except KeyError:
            continue
            
    if returnDict:
        return mask, sql, fid, sqlDict
    else:
        return mask, sql, fid
    
def loadVideo(video_id, print_info=False, print_time=False,):
    
    camera_id = video_id[1]
    if video_id[2] == "1":
        frame_size = "640x480"
    else:
        frame_size = "320x240"
    video_id = video_id[0]
    
    f2 = video_id[:2]
    f1 = f2[:1]
    #print(f1,f2)
    if print_time:
        time = datetime.now()

    path = '/afs/inf.ed.ac.uk/group/ug4-projects/s1413557/summaries/{0}/{01}/'.format(f1,f2)
    path2 = '/afs/inf.ed.ac.uk/group/ug4-projects/s1413557/sqldump/{0}/{01}/'.format(f1,f2)
    if os.name == "nt":
        path = 'E:/f4k_extracted_image/output/summaries/{0}/{01}/'.format(f1,f2)
        path2 = 'E:/f4ktable/{0}/{01}/'.format(f1,f2)
    
    headm = 'summary_'
    tailm = '.avi'
    headc = 'frame_info_'
    tailc = '.txt'
    movie = path + headm + video_id + tailm
    csv = path + headc + video_id + tailc
    sql = path2 + video_id + tailc

    if print_time:
        time = datetime.now()
    
    frame_info = np.genfromtxt(csv, delimiter=',',dtype=int)
    
    if len(frame_info) == 0:
        if print_info:
            print("NO DETECTION IN VIDEO: {0}!".format(video_id))
        return ([], [], [], [], [], 0)
    
    if len(frame_info.shape) == 1:
        #I HATE YOU NP
        frame_info = np.array([frame_info])
    
    clip = VideoFileClip(movie)
    fps = clip.fps
    duration = clip.duration
    frames = int(fps * duration)
    hasContour, contour, fish_id = loadSql(sql, frame_info)
    
    #Take out RGB arrays before stuff?
    #Replace clip reader with list, so dont have to delete stuff everytime.
    
    
    RGB = [None] * frames
    for i in range(frames):
        RGB[i] = clip.get_frame(i / clip.fps)
    
    if frames != len(frame_info[:,0]):
        RGB.append(clip.get_frame(frames / clip.fps))
        frames += 1
    
    if not(clip==[]):
        clip.reader.close()
    del clip
    
    if print_info:
        if print_time:
            print('Loading data took: {}'.format(datetime.now() - time))
        print('Using video_id: {0}'.format(video_id))
        print('Using movie, csv, sql paths: \n{0}\n{1}\n{2}'.format(movie,csv,sql))
        print('Video frame size: {0}, camera_id: {1}'.format(frame_size,camera_id))
        print('Total frames in video: {0}'.format(frames))
        count1 = sum(hasContour)
        count2 = len(hasContour)
        print("{0} out of {1}, about {2} detection have a bounding box in sql."
              .format(count1,count2,"{0:.0f}%".format(count1/(count2*1.0) * 100)))
        
    if print_time:
        time = datetime.now()
        throw = 0
        keep = 0
        tot = 0
        for i in range(frames):
            if hasContour[i]:
                cline = contour[i]
                result = FEIF(cline,case=frame_size,matt_mode=True)
                if result:
                    throw += 1
                else:
                    keep += 1
                tot += 1
        if print_info and tot != 0:
            print('{0} out of {1} total detection is rejected by FEIF, {2} kept. Reject rate: {3}'
                  .format(throw,tot,keep,"{0:.0f}%".format(throw/(tot*1.0) * 100)))
            print('FEIF Runtime: {}'.format(datetime.now() - time))
    
    return (frame_info, RGB, hasContour, contour, fish_id, frames)

