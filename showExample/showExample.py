from __future__ import print_function

import os
import sys
import numpy as np
import moviepy as mp
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from moviepy.editor import *
from bitarray import bitarray

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
    
    if return_what == "Both":
        return (points2, points3)
    if return_what == "Original":
        return points3
    return points2

def cleanLine(a):
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
        raise Exception('String Not Long Enough')
    contX = int(string[0:11],2)
    contY = int(string[11:22],2)
    contH = int(string[22:32],2)
    contW = int(string[32:42],2)
    firstXPoint = int(string[42:53],2)
    padding = int(string[53:56],2)
    string2 = string[56:]
    return (contX, contY, contW, contH, firstXPoint, padding, string2)

def loadResults(video_id):
    video_id = video_id[0]
    f2 = video_id[:2]
    f1 = f2[:1]
    tailYHAT = ".YHAT.npy"
    tailFINAL = ".RESULT.npy"
    path = os.path.dirname(os.path.realpath(__file__)) + '/output/{0}/{01}/'.format(f1,f2)
    path2 = os.path.dirname(os.path.realpath(__file__)) + '/final/{0}/{01}/'.format(f1,f2)
    
    yhat = np.load(path + video_id + tailYHAT)
    result = np.load(path2 + video_id + tailFINAL)
    print('Using result paths: \n{0}\n{1}'.format(path + video_id + tailYHAT,path2 + video_id + tailFINAL))
    return (yhat, result)
    

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

def loadVideo(video_id):
    
    if video_id[2] == "1":
        frame_size = "640x480"
    else:
        frame_size = "320x240"
        
    camera_id = video_id[1]
    video_id = video_id[0]
    f2 = video_id[:2]
    f1 = f2[:1]
    headm = 'summary_'
    tailm = '.avi'
    headc = 'frame_info_'
    tailc = '.txt'
    #TODO: Change the directory if you want to open files somewhere else.
    path = os.path.dirname(os.path.realpath(__file__)) + '/f4k_extracted_image/output/summaries/{0}/{01}/'.format(f1,f2)
    path2 = os.path.dirname(os.path.realpath(__file__)) + '/f4ktable/{0}/{01}/'.format(f1,f2)
    movie = path + headm + video_id + tailm
    csv = path + headc + video_id + tailc
    sql = path2 + video_id + tailc
    
    print('Using movie, csv, sql paths: \n{0}\n{1}\n{2}'.format(movie,csv,sql))
    print('Video frame size: {0}, camera_id: {1}'.format(frame_size,camera_id))
    
    frame_info = np.genfromtxt(csv, delimiter=',',dtype=int)
    
    if len(frame_info) == 0:
        print("NO DETECTION IN VIDEO: {0}!".format(video_id))
        return ([], [], [], [], [], 0)
    
    if len(frame_info.shape) == 1:
        frame_info = np.array([frame_info])
    
    clip = VideoFileClip(movie)
    fps = clip.fps
    duration = clip.duration
    frames = int(fps * duration)
    hasContour, contour, fish_id = loadSql(sql, frame_info)
    
    RGB = [None] * frames
    for i in range(frames):
        RGB[i] = clip.get_frame(i / clip.fps)
    
    if frames != len(frame_info[:,0]):
        RGB.append(clip.get_frame(frames / clip.fps))
        frames += 1
    
    if not(clip==[]):
        clip.reader.close()
    del clip
    
    print('Total frames in video: {0}'.format(frames))
    
    return (frame_info, RGB, hasContour, contour, fish_id, frames)

def loadMovids():
    path = os.path.dirname(os.path.realpath(__file__)) + '/misc/movie_ids_info.txt'
    with open(path) as f:
        movs = f.readlines()
    return np.array([x.strip().split(",") for x in movs])

def loadLengths():
    path = os.path.dirname(os.path.realpath(__file__)) + '/misc/vidLen.txt'
    with open(path) as f:
        movs = f.readlines()
    return np.array([int(x.strip()) for x in movs])

def requestInput():
    print("")
    print("Usage: python ./showExample.py <video>")
    print("")
    print("The <video> field can use the following format:")
    print("  VIDEO_ID of the video, for example:")
    print("    00000857dd49007f4a35abebb90aafe0#201110011530")
    print("    00000857dd49007f4a35abebb90aafe0")
    print("  Number of the video, from 1 to 396901:")
    print("    192039")
    print("")
    print("Example: python ./showExample.py 5")
    print("")
    
def main():
    
    #Check inputs
    if len(sys.argv) < 2:
        requestInput()
        return
    
    #Load video lists.
    arg = sys.argv[1]
    movs = loadMovids()
    movs_length = loadLengths()
    
    #Check inputs
    if len(arg)==45:
        for i in range(396901):
            if movs[i][0] == arg:
                movid = i
    elif len(arg)==32:
        for i in range(396901):
            if movs[i][0][:32] == arg:
                movid = i
    elif len(arg)<=6:
        try:
            movid = int(arg) - 1
            if movid < 0:
                print("\nWrong Input Format!")
                requestInput()
                return
        except:
            print("\nWrong Input Format!")
            requestInput()
            return
    else:
        print("\nWrong Input Format!")
        requestInput()
        return
    
    #Check if video is found.
    try:
        print("\nUsing movid: {}".format(movs[movid][0]))
    except:
        print("\nInput Video_ID Not Found!")
        requestInput()
        return
    
    #Load data
    try:
        info, clip, hasContour, contour, fish_id, frames = loadVideo(movs[movid])
    except:
        print("\nLoading Data Failed!")
        return
        
    if frames == 0:
        print("This video have no frames!")
        return
    
    try:
        yhat, result = loadResults(movs[movid])
    except:
        print("Loading Classification Result Failed!")
        return
    
    
    #Actual Plotting
    for i in range(frames):
        
        cline = contour[i]
        extractMeta(cline, print_values=True)
        thisContour, cont2 = getContour(cline, return_what="Both")
        
        fig = plt.figure(figsize=(4,4))
        plt.imshow(clip[i])
        plt.scatter(thisContour[:,0],thisContour[:,1],s=1,color='blue')
        
        if np.sum(yhat[i,:,1]) > 3.999:
            plt.xlabel("This Frame is rejected by Plankton Removal")
        elif np.sum(yhat[i,:,6]) > 3.999:
            plt.xlabel("This Frame is rejected by FEIF")
            x,y = np.min(cont2,0)
            if movs[movid][2]=="1" and x <= 266 and y <= 33:
                plt.gca().add_patch(patches.Rectangle((0,0),266-x+10,33-y+10,fill=False,linewidth=1,color='red'))
                plt.xlabel("This Frame is rejected by FEIF timestamp")
            if movs[movid][2]=="0" and x <= 163 and y <= 16:
                plt.gca().add_patch(patches.Rectangle((0,0),163-x+10,16-y+10,fill=False,linewidth=1,color='red'))
                plt.xlabel("This Frame is rejected by FEIF timestamp")
        elif result[i]:
            plt.xlabel("This Frame Classified as Fish\nWith SVM class 6 probability: {0:.0f}%".format(yhat[i,0,5]*100))
        else:
            plt.xlabel("This Frame Classified as Non-Fish\nWith SVM class 6 probability: {}".format(yhat[i,0,5]*100))
            
        
        plt.xticks([])
        plt.yticks([])
        plt.show()
        #Below code sometimes stuck
        #plt.draw()
        #plt.waitforbuttonpress(0) # this will wait for indefinite time
        #plt.close(fig)

if __name__ == "__main__":
    main()
