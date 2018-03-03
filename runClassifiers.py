#!/afs/inf.ed.ac.uk/user/s14/s1413557/miniconda2/bin/python

from __future__ import print_function

import time as sleeptime
from mpi4py import MPI
from mpi.master_slave import Master, Slave
from mpi.work_queue import WorkQueue
from f4klib import *
import multiprocessing
import lutorpy as lua

#HOSTS=basso,battaglin,belloni,bergamaschi,berrendero,bertoglio,berzin,binda
#mpiexec -n 16 -host $HOSTS python ~/f4k/runMulticoreFeatureExtract.py


class MyApp(object):

    def __init__(self, slaves):
        self.master = Master(slaves)
        self.work_queue = WorkQueue(self.master)

    def terminate_slaves(self):
        self.master.terminate_slaves()

    def run(self):
        
        time = datetime.now()
        movs = loadMovids()
        movs_length = loadLengths()
        
        #13b: 30598-30695
        
        #0: 0-24941
        #1: 24941-49433
        #2: 49433-74100
        #3: 74100-99012
        #4: 99012-123658
        #5: 123658-148701
        #6: 148701-173761
        #7: 173761-198372
        #8: 198372-223132
        #9: 223132-247825
        #a: 247825-272495
        #b: 272495-297592
        #c: 297592-322424
        #d: 322424-347142
        #e: 347142-372011
        #f: 372011-396901
        
        start = 322424
        end = 396901
        
        #Put longer task at start.
        if end == 396901:
            order = np.argsort(movs_length[start:])
        else:
            order = np.argsort(movs_length[start:end])
        
        #For statistics
        totWork = 0#end - start
        completed = 0
        
        #idl = np.hstack((np.arange(30598,30633),np.arange(30634,30638)))
        #idl = np.array([396853,396857,396859,396860,396866,396876,396880,396892,396895,396900,
        #        396823,396829,396843,396852,396862,396870,396882,396885,396889,396894,
        #        396856,396863,396864,396868,396869,396893,396896,396897,396898,396899,
        #        396624,396639,396662,396675,396728,396737,396759,396777,396790,396804,
        #        396750,396760,396767,396784,396792,396793,396872,396877,396878,396886,
        #        396824,396836,396839,396854,396858,396861,396865,396871,396874,396884,
        #        396720,396733,396778,396815,396820,396827,396830,396834,396879,396890,
        #        396840,396841,396845,396849,396850,396851,396867,396883,396887,396891,
        #        396785,396802,396811,396822,396838,396844,396873,396875,396881,396888])
        #order = np.argsort(movs_length[idl])
        #for i in idl[order]:
        
        for i in np.arange(start,end)[order]:
            
            #Alternative to early removal, so it wont thrash stuff.
            if movs_length[i] > 50000:
                idee = movs[i][0]
                savepath = "/afs/inf.ed.ac.uk/group/project/F4KC/output/{0}/{1}/{2}"
                savepath = savepath.format(idee[0],idee[0:2],idee)
                
                if not os.path.isfile(savepath+".COMPLETE.npy"):
                    print("Master removes movid {0} with early removal".format(movs[i][0]))
                    yhat = np.zeros((movs_length[i],4,10))
                    yhat[:,:,1] = 1
                    np.save(savepath+".YHAT",yhat)
                    np.save(savepath+".COMPLETE",np.array([]))
               
            totWork += 1
            movid = movs[i]
            self.work_queue.add_work(data=('Do stuff', movid))

       
        while not self.work_queue.done():

            self.work_queue.do_work()

            #
            # reclaim returned data from completed slaves
            #
            for slave_return_data in self.work_queue.get_completed_work():
                done, message, movidf = slave_return_data
                if done:
                    if message == "FAILED":
                        self.work_queue.add_work(data=('Do stuff', movidf))
                    else:
                        completed += 1
                        print("Progress: {0}/{1}, took {2}. {3}"
                          .format(str(completed).rjust(6),str(totWork).rjust(6),str(datetime.now()-time),message))

            # sleep some time
            sleeptime.sleep(0.001)

class MySlave(Slave):
    """
    A slave process extends Slave class, overrides the 'do_work' method
    and calls 'Slave.run'. The Master will do the rest
    """

    def __init__(self):
        super(MySlave, self).__init__()
        self.svm = pickle.load(open('/afs/inf.ed.ac.uk/group/ug4-projects/s1413557/svmObject', 'rb'))
           
    def run(self):
        super(MySlave, self).run()
        try:
            self.p.terminate()
            print(MPI.Get_processor_name().split(".")[0] + "'s subprocess killed!")
        except Exception:
            print(MPI.Get_processor_name().split(".")[0] + "'s subprocess killing failed!")
            
    def do_work(self, data):
        
        q = multiprocessing.Queue()
        self.p = multiprocessing.Process(target=do_actual_work, args=(self,data,q,))
        self.p.start()
        ret = q.get()
        self.p.join()
        return (ret[0],ret[1],ret[2])
        

def do_actual_work(self, data, q):
    rank = MPI.COMM_WORLD.Get_rank()
    name = MPI.Get_processor_name().split(".")[0].ljust(12)
    task, movid = data
    idee = movid[0]
    fname = movid[0].split("#")[0]
    
    savepath = "/afs/inf.ed.ac.uk/group/project/F4KC/output/{0}/{1}/{2}".format(idee[0],idee[0:2],idee)

    #Check if video is already extracted.
    if os.path.isfile(savepath+".COMPLETE.npy"):
        q.put([True, 'Slave: %s skipped   %s because it\'s done.' % (name, idee), movid])
        return

    #Load the video
    time = datetime.now()
    info, clip, hasContour, contour, fish_id, frames = loadVideo(movid, alt_path=True)

    #Skipping empty videos
    if frames == 0:
        #Skipping stuff
        #print('Slave: %s skipped an empty video "%s"' % (name, idee))
        np.save(savepath+".COMPLETE",np.array([]))
        q.put([True, 'Slave: %s skipped   %s because it\'s empty' % (name, idee), movid])
        return

    #Notify the Boss
    print(" " * 46 + 'Slave: {0} started   {1} with {2} frames'.format(name, idee, str(frames).ljust(6)))
    
    yhat = np.zeros((frames,4,10))
    featurepath = "/afs/inf.ed.ac.uk/group/project/F4KC/features/{0}/{1}/{2}".format(idee[0],idee[0:2],idee)
    
    if earlyRemoval(movid, frames):
        #Set probability of class 2 to 1.
        yhat[:,:,1] = 1
    elif not os.path.isfile(featurepath+".feif.npy"):
        #Set probability of class 7 to 1.
        yhat[:,:,6] = 1
    else: #Normal case
        features = np.load(featurepath+".pcaFeature.npy")
        feifmask = np.load(featurepath+".feif.npy")
        yhat[np.bitwise_not(feifmask),:,6] = 1
    
        #========== SVM ==========
        
        yhat[feifmask,0,:] = self.svm.predict_proba(features[:,:80])
    
        #========== CNN ==========
        #initialize for CNN
        require('nn')
        require('image')
        meann = [[0.5, 0.5, 0.5],
                 [0.39652687546177, 0.45261265063944, 0.42062426025794], #'N_SGD'
                 [0.9249023692381,  0.92963844758093, 0.92607431571841], #'W_C_SGD'
                 [0.048790299759605,0.052937559625764,0.049839084833519]]#'B_C_SGD'
        stdd = [[0.25, 0.25, 0.25],
                [0.28132888018719, 0.30690810636064, 0.30367700787976],#'N_SGD'
                [0.21736589663274, 0.20606532102447, 0.21408039791867],#'W_C_SGD'
                [0.15689543246897, 0.16453823057925, 0.15784736844257]]#'B_C_SGD'
        
        neighbourhood = image.gaussian1D(13)
        normalization = nn.SpatialContrastiveNormalization(1, neighbourhood, 1)._float()
        model1 = torch.load('/afs/inf.ed.ac.uk/user/s14/s1413557/f4k/lua/models/float/N_SGD.model.net')
        fmodel1 = model1._float()
        model2 = torch.load('/afs/inf.ed.ac.uk/user/s14/s1413557/f4k/lua/models/float/W_C_SGD.model.net')
        fmodel2 = model2._float()
        model3 = torch.load('/afs/inf.ed.ac.uk/user/s14/s1413557/f4k/lua/models/float/B_C_SGD.model.net')
        fmodel3 = model3._float()
            
        for f in range(frames):
            
            if not feifmask[f]:
                continue
                
            image_N = clip[f]
            #This is by far the worst bug ive seen.
            image_N = cv2.cvtColor(image_N, cv2.COLOR_RGB2BGR)

            image_contour = getContour(contour[f])
            mask = np.full(image_N.shape, 0, dtype=np.uint8)
            cv2.fillPoly(mask, np.int32([image_contour]), (255,)*3)
            image_BC = cv2.bitwise_and(mask,image_N)
            image_WC = cv2.bitwise_or(cv2.bitwise_not(mask),image_N)

            w, h = (89 - np.max(image_contour,0)) / 2
            image_BC = np.roll(image_BC, w, axis=1)
            image_BC = np.roll(image_BC, h, axis=0)
            image_WC = np.roll(image_WC, w, axis=1)
            image_WC = np.roll(image_WC, h, axis=0)

            #Image_N
            xt = torch.fromNumpyArray(np.transpose(image_N,(2,0,1)).astype(np.double)/255.0)._float()
            xt = image.rgb2yuv(xt)
            for i in range(3):
                xt[i]._add(-meann[1][i])
                xt[i]._div(stdd[1][i])
                xt[i] = normalization._forward(nn.utils.addSingletonDimension(xt[i],1))
            yt = fmodel1._forward(xt)
            yn = yt.asNumpyArray()
            yhat[f,1,:] = np.exp(yn)
            del xt,yt,yn

            #Image_W_C
            xt = torch.fromNumpyArray(np.transpose(image_WC,(2,0,1)).astype(np.double)/255.0)._float()
            xt = image.rgb2yuv(xt)
            for i in range(3):
                xt[i]._add(-meann[2][i])
                xt[i]._div(stdd[2][i])
                xt[i] = normalization._forward(nn.utils.addSingletonDimension(xt[i],1))
            yt = fmodel2._forward(xt)
            yn = yt.asNumpyArray()
            yhat[f,2,:] = np.exp(yn)
            del xt,yt,yn

            #Image_B_C
            xt = torch.fromNumpyArray(np.transpose(image_BC,(2,0,1)).astype(np.double)/255.0)._float()
            xt = image.rgb2yuv(xt)
            for i in range(3):
                xt[i]._add(-meann[3][i])
                xt[i]._div(stdd[3][i])
                xt[i] = normalization._forward(nn.utils.addSingletonDimension(xt[i],1))
            yt = fmodel3._forward(xt)
            yn = yt.asNumpyArray()
            yhat[f,3,:] = np.exp(yn)
            del xt,yt,yn
        
     
            
    np.save(savepath+".YHAT",yhat)
    np.save(savepath+".COMPLETE",np.array([]))

    retString = "Slave: {0} completes {1} with {2} frames in {3}"
    retString = retString.format(name, idee, str(frames).ljust(6), str(datetime.now()-time))

    q.put([True, retString, movid])
    return
    
    
def main():

    name = MPI.Get_processor_name()
    rank = MPI.COMM_WORLD.Get_rank()
    size = MPI.COMM_WORLD.Get_size()
    os.nice(19)

    print('I am  %s rank %d (total %d)' % (name, rank, size) )

    if rank == 0: # Master

        app = MyApp(slaves=range(1, size))
        app.run()
        app.terminate_slaves()

    else: # Any slave

        MySlave().run()

    print('Task completed (rank %d)' % (rank) )

if __name__ == "__main__":
    main()

