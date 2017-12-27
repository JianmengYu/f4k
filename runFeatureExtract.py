#!/afs/inf.ed.ac.uk/user/s14/s1413557/miniconda2/bin/python

from __future__ import print_function
from f4klib import *

time = datetime.now()

session = pymatlab.session_factory('matlab -nojvm -nodisplay')
session.run('cd /afs/inf.ed.ac.uk/user/s14/s1413557/f4k-2017-msc-master/matt-msc/workspace/f4k/fish_recog')

print("Initialize Matlab took {0}".format(datetime.now() - time) )
time = datetime.now()

movs = loadMovids()
picker = 6
movid = movs[picker]
info, clip, hasContour, contour, fish_id, frames = loadVideo(movid)

time = datetime.now()
f4kfeatures = np.zeros((frames,2626))
feif_result = np.zeros(frames, dtype=bool)

shadyes = 0
shadno = 0
shadwhat = 0

print("Initialize Input took {0}".format(datetime.now() - time) )
time = datetime.now()

print("There is a total of {0} of frames".format(frames))

for i in range(frames):
    if hasContour[i]:
        if not FEIF(contour[i]):
            shadyes += 1
            feif_result[i] = True
            thiscontour = getContour(contour[i])
            image = clip[i]
            full_fish = np.full((100,100), 0, dtype=np.uint8)
            cv2.fillPoly(full_fish, np.array([thiscontour], dtype=np.int32), (255,))
            session.putvalue('A',image)
            session.putvalue('B',full_fish)
            session.run('C = feature_generateFeatureVector(A,B,false)')
            f4kfeatures[i,:] = session.getvalue('C')
        else:
            shadno += 1
    else:
        shadwhat += 1
    print("Process {0} image took {1}".format(i+1,datetime.now() - time), end='\r')

print("Took a total of {0}           ".format(datetime.now() - time) )
print("Only {1}, {0:.3f}% of the features are calculated.".format(100.0*shadyes/frames,shadyes))

time = datetime.now()
hasContour = feif_result

mattFeatures = getMattFeatures(info, clip, hasContour, contour, fish_id, print_info=True, ret_normalized_erraticity=False)

print("Calculating Matt Feature took {0}".format(datetime.now() - time) )
time = datetime.now()

idee = movid[0]
savepath = "/afs/inf.ed.ac.uk/group/ug4-projects/s1413557/features/{0}/{1}/{2}".format(idee[0],idee[0:2],idee)
np.save(savepath+".f4kfeature",f4kfeatures)
np.save(savepath+".mattfeature",mattFeatures)
np.save(savepath+".feif",feif_result)

del session
