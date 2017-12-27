#!/afs/inf.ed.ac.uk/user/s14/s1413557/miniconda2/bin/python

from __future__ import print_function #ffs
from f4klib import *

session = pymatlab.session_factory()
session.run('cd /afs/inf.ed.ac.uk/user/s14/s1413557/f4k-2017-msc-master/matt-msc/workspace/f4k/fish_recog')

movs = loadMovids()
picker = 6
movid = movs[picker]
info, clip, hasContour, contour, fish_id, frames = loadVideo(movid)

time = datetime.now()
for i in range(10):
    thiscontour = getContour(contour[i])
    image = clip[i]
    full_fish = np.full((100,100), 0, dtype=np.uint8)
    cv2.fillPoly(full_fish, np.array([thiscontour], dtype=np.int32), (255,))
    session.putvalue('A',image)
    session.putvalue('B',full_fish)
    session.run('C = feature_generateFeatureVector(A,B,false)')
    c = session.getvalue('C')
    print(c)
    print("Process {0} image took {1}".format(i,datetime.now() - time), end='\r')
print("Took a total of {0}           ".format(datetime.now() - time) )

del session
