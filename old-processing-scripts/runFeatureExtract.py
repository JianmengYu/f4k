#!/afs/inf.ed.ac.uk/user/s14/s1413557/miniconda2/bin/python

from __future__ import print_function
from f4klib import *

session = pymatlab.session_factory('matlab -nojvm -nodisplay')
session.run('cd /afs/inf.ed.ac.uk/user/s14/s1413557/f4k-2017-msc-master/matt-msc/workspace/f4k/fish_recog')

movs = loadMovids()
picker = 5
movid = movs[picker]
info, clip, hasContour, contour, fish_id, frames = loadVideo(movid)

f4kfeatures = np.zeros((frames,2626))
feif_result = np.zeros(frames, dtype=bool)

if movid[2] == "1":
    frame_size = "640x480"
else:
    frame_size = "320x240"

for i in range(frames):
    if hasContour[i]:
        if not FEIF(contour[i], frame_size, matt_mode=True):
            shadyes += 1
            feif_result[i] = True
            thisContour = np.int32([getContour(contour[i])])
            image = clip[i]
            full_fish = np.full((100,100), 0, dtype=np.uint8)
            cv2.fillPoly(full_fish, thisContour, (255,))
            session.putvalue('A',image)
            session.putvalue('B',full_fish)
            session.run('C = feature_generateFeatureVector(A,B,false)')
            f4kfeatures[i,:] = session.getvalue('C')

mattFeatures = getMattFeatures(info, clip, hasContour, contour, fish_id, print_info=False, ret_normalized_erraticity=False)

idee = movid[0]
savepath = "/afs/inf.ed.ac.uk/group/ug4-projects/s1413557/features/{0}/{1}/{2}".format(idee[0],idee[0:2],idee)
np.save(savepath+".f4kfeature",f4kfeatures)
np.save(savepath+".mattfeature",mattFeatures)
np.save(savepath+".feif",feif_result)

del session
