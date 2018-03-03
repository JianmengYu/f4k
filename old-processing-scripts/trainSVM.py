#!/afs/inf.ed.ac.uk/user/s14/s1413557/miniconda2/bin/python

from __future__ import print_function
from f4klib import *
from sklearn.svm import SVC

import os
import time as sleeptime
os.nice(19)
path = '/afs/inf.ed.ac.uk/group/ug4-projects/s1413557/svmObject'



print("Loading ...")

features,targets = loadTrainDataSet(includeNew=False)
features = features[:,:80]

print("Loading Done")
sleeptime.sleep(1)



print("Training ...")

final_svm = SVC(kernel='rbf', gamma=0.001, C=1, probability=True, class_weight='balanced')

final_svm.fit(features,targets.astype('int'))

print("Training Done")
sleeptime.sleep(1)




print("Dumping ...")

pickle.dump(final_svm, open(path, 'wb'))

print("Dumping Done")
