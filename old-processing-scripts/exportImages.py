from __future__ import print_function
from f4klib2 import *
movs = loadMovids()
movs_length = loadLengths()
printCameras()

idl = np.hstack((np.arange(30598,30633),np.arange(30634,30638)))

for i in idl:
    movid = movs[i]
    info, clip, hasContour, contour, fish_id, frames = loadVideo(movid)
    
    try:
        os.makedirs("/afs/inf.ed.ac.uk/group/project/F4KC/image_N/" + movid[0] + "/")
        os.makedirs("/afs/inf.ed.ac.uk/group/project/F4KC/image_BC/" + movid[0] + "/")
        os.makedirs("/afs/inf.ed.ac.uk/group/project/F4KC/image_WC/" + movid[0] + "/")
    except Exception:
        waa = 1
    
    for f in range(frames):
        image_N = clip[f]
        #cv2.imwrite("/afs/inf.ed.ac.uk/group/project/F4KC/temp/" + fname + "/" + str(f) + ".jpg", image_N)
        #image_N = cv2.imread("/afs/inf.ed.ac.uk/group/project/F4KC/temp/" + fname + "/" + str(f) + ".jpg")
        #MATT! MATT!
        #image_N = cv2.cvtColor(image_N, cv2.COLOR_RGB2BGR)

        image_contour = getContour(contour[f])
        mask = np.full(image_N.shape, 0, dtype=np.uint8)
        cv2.fillPoly(mask, np.int32([image_contour]), (255,)*3)
        
        #89 or 90?
        w, h = (89 - np.max(image_contour,0)) / 2

        image_BC = cv2.bitwise_and(mask,image_N)
        image_WC = cv2.bitwise_or(cv2.bitwise_not(mask),image_N)
        
        image_BC = np.roll(image_BC, w, axis=1)
        image_BC = np.roll(image_BC, h, axis=0)
        image_WC = np.roll(image_WC, w, axis=1)
        image_WC = np.roll(image_WC, h, axis=0)
        
        
        image_N = cv2.cvtColor(image_N, cv2.COLOR_RGB2BGR)
        image_BC = cv2.cvtColor(image_BC, cv2.COLOR_RGB2BGR)
        image_WC = cv2.cvtColor(image_WC, cv2.COLOR_RGB2BGR)
        
        cv2.imwrite("/afs/inf.ed.ac.uk/group/project/F4KC/image_N/" +movid[0]+"/"+str(f)+".png", image_N)
        cv2.imwrite("/afs/inf.ed.ac.uk/group/project/F4KC/image_BC/"+movid[0]+"/"+str(f)+".png", image_BC)
        cv2.imwrite("/afs/inf.ed.ac.uk/group/project/F4KC/image_WC/"+movid[0]+"/"+str(f)+".png", image_WC)
    print("Finished Exporting Video {0}".format(i))


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
    movid = movs[i]
    info, clip, hasContour, contour, fish_id, frames = loadVideo(movid)
    
    try:
        os.makedirs("/afs/inf.ed.ac.uk/group/project/F4KC/image_N/" + movid[0] + "/")
        os.makedirs("/afs/inf.ed.ac.uk/group/project/F4KC/image_BC/" + movid[0] + "/")
        os.makedirs("/afs/inf.ed.ac.uk/group/project/F4KC/image_WC/" + movid[0] + "/")
    except Exception:
        waa = 1
    
    if frames > 100: frames = 100
    
    for f in range(frames):
        image_N = clip[f]
        #cv2.imwrite("/afs/inf.ed.ac.uk/group/project/F4KC/temp/" + fname + "/" + str(f) + ".jpg", image_N)
        #image_N = cv2.imread("/afs/inf.ed.ac.uk/group/project/F4KC/temp/" + fname + "/" + str(f) + ".jpg")
        #MATT! MATT!
        #image_N = cv2.cvtColor(image_N, cv2.COLOR_RGB2BGR)

        image_contour = getContour(contour[f])
        mask = np.full(image_N.shape, 0, dtype=np.uint8)
        cv2.fillPoly(mask, np.int32([image_contour]), (255,)*3)
        
        #89 or 90?
        w, h = (89 - np.max(image_contour,0)) / 2

        image_BC = cv2.bitwise_and(mask,image_N)
        image_WC = cv2.bitwise_or(cv2.bitwise_not(mask),image_N)
        
        image_BC = np.roll(image_BC, w, axis=1)
        image_BC = np.roll(image_BC, h, axis=0)
        image_WC = np.roll(image_WC, w, axis=1)
        image_WC = np.roll(image_WC, h, axis=0)
        
        
        image_N = cv2.cvtColor(image_N, cv2.COLOR_RGB2BGR)
        image_BC = cv2.cvtColor(image_BC, cv2.COLOR_RGB2BGR)
        image_WC = cv2.cvtColor(image_WC, cv2.COLOR_RGB2BGR)
        
        cv2.imwrite("/afs/inf.ed.ac.uk/group/project/F4KC/image_N/" +movid[0]+"/"+str(f)+".png", image_N)
        cv2.imwrite("/afs/inf.ed.ac.uk/group/project/F4KC/image_BC/"+movid[0]+"/"+str(f)+".png", image_BC)
        cv2.imwrite("/afs/inf.ed.ac.uk/group/project/F4KC/image_WC/"+movid[0]+"/"+str(f)+".png", image_WC)
    print("Finished Exporting Video {0}".format(i))

