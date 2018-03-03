from __future__ import print_function
from f4klib2 import *
movs = loadMovids()
movs_length = loadLengths()

idl = np.hstack((np.arange(30598,30633),np.arange(30634,30638)))

for i in idl:
    movid = movs[i][0]
    frames = movs_length[i]
    try:
        gts = loadGT(movid, frames, partial=True)
    except:
        gts = loadGT(movid, frames, partial=False)
    
    for f in range(frames):

        if gts[f] == 0: continue
        print("{0}/{1}.png,{2}".format(movid,f,gts[f]))

forty = [112,180,272,285,330,       447,469,474,498,500,
         517,527,545,550,622,       661,713,720,749,771,
         779,806,807,902,959,       970,982,1038,1042,1068,
         1085,1100,1111,1114,1116,  1136,1147,1155,1211,1258,
         1306,1373,1379,1409,1432,  1505]
fortyone = [10,33,75,82,101,           114,182,183,275,279,
            282,291,306,325,338,       380,420,424,449,482,
            490,518,560,579,593,       616,652,657,685,695,
            701,737,740,793,803,       811,834,843,844,858,
            868,923,931,955,966,       1029,1030,1156,1160,1187, 
            1193,1223,1241,1278,1279,  1281,1323,1356,1361,1366,
            1378,1413,1428,1491,1493,  1513,1530,1535]

idl = np.hstack((np.array(forty),np.array(fortyone)))

for i in idl:
    movid = movs[i][0]
    frames = movs_length[i]
    gts = loadNewGT(movid, frames)
    if frames > 100: frames = 100
    
    for f in range(frames):
        print("{0}/{1}.png,{2}".format(movid,f,gts[f]))
