#!/afs/inf.ed.ac.uk/user/s14/s1413557/miniconda2/bin/python

from __future__ import print_function

import time as sleeptime
from mpi4py import MPI
from mpi.master_slave import Master, Slave
from mpi.work_queue import WorkQueue
from f4klib import *
import shutil

#HOSTS=basso,battaglin,belloni,bergamaschi,berrendero,bertoglio,berzin,binda
#mpiexec -n 16 -host $HOSTS python ~/f4k/runMulticoreFeatureExtra


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
        start = 30598
        end = 30695
        
        #Put longer task at start.
        order = np.argsort(movs_length[start:end])
        
        #For statistics
        totWork = end - start
        completed = 0
        
        for i in np.arange(start,end)[order]:
            movid = movs[i]
            #It's modified that task is appended at front
            self.work_queue.add_work(data=('Do stuff', movid))

                
        #for i in range(tasks):
        #    self.work_queue.add_work(data=('Do stuff', i))
       
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

    def do_work(self, data):
        rank = MPI.COMM_WORLD.Get_rank()
        name = MPI.Get_processor_name().split(".")[0].ljust(12)
        
        task, movid = data
        idee = movid[0]
        fname = movid[0].split("#")[0]
        savepath = "/afs/inf.ed.ac.uk/group/ug4-projects/s1413557/features_sample/{0}/{1}/{2}".format(idee[0],idee[0:2],idee)
        
        #Check if video is already extracted.
        if os.path.isfile(savepath+".COMPLETE.npy"):
            return (True, 'Slave: %s skipped   %s because it\'s done.' % (name, idee), movid)
    
        #Load the video
        time = datetime.now()
        info, clip, hasContour, contour, fish_id, frames = loadVideo(movid)
        
        #Skipping empty videos
        if frames == 0:
            #Skipping stuff
            #print('Slave: %s skipped an empty video "%s"' % (name, idee))
            np.save(savepath+".COMPLETE",np.array([]))
            return (True, 'Slave: %s skipped   %s because it\'s empty' % (name, idee), movid)
        
        print('                                              Slave: {0} started   {1} with {2} frames'
              .format(name, idee, str(frames).ljust(6)))
        
        #Prevent Repeat Opening Matlab
        try: session
        except NameError: session = None
        if session is None:
            try:
                session = pymatlab.session_factory('matlab -nodisplay')
                session.run('cd /afs/inf.ed.ac.uk/user/s14/s1413557/f4k-2017-msc-master/matt-msc/workspace/f4k/fish_recog')
                #ASHBURY CRASHES A LOT WHEN USING 40 POOLS, HES NOT SO GREAT AFTERALL
                if name[:7] == "ashbury":
                    #Our HERO, the MAGNIFICENT and MOST EDUCATIONAL sir ASHBURY, the ROYAL CLUSTA with FOURTY EXTRAVAGANZA PROCESSORS.
                    #print("ACTIVATE SPELL CARD: POOL40!")
                    session.run("pc = parcluster('local');")
                    session.run('pc.NumWorkers = 40;')
                    session.run('parpool(40);')
                    #I hope people working on it wont hate me.
            except Exception:
                print("Slave {0} failed! On Task {1}! initializing MATLAB".format(name, idee))
                if name[:7] == "ashbury":
                    try:
                        #This folder fuck things up
                        shutil.rmtree("/afs/inf.ed.ac.uk/user/s14/s1413557/.matlab/local_cluster_jobs/")
                    except Exception:
                        print("Slave {0} failed! Job folder can't be removed!".format(name))
                return (True, "FAILED", movid)
          
        #FEIF
        if movid[2] == "1":frame_size = "640x480"
        else:frame_size = "320x240"
        feif_result = np.zeros(frames, dtype=bool)
        for i in range(frames):
            if hasContour[i]:
                if not FEIF(contour[i], frame_size, matt_mode=True):
                    feif_result[i] = True
               
        if np.sum(feif_result) == 0:
            #Skipping stuff
            #print('Slave: %s skipped an empty video "%s"' % (name, idee))
            np.save(savepath+".COMPLETE",np.array([]))
            return (True, 'Slave: %s skipped   %s because it\'s all rejected' % (name, idee), movid)

        #Setting up features need to be computed
        hasCL = np.sum(feif_result)
        rgbImgs = [None]*hasCL
        binImgs = [None]*hasCL
        index = 0
        for i in range(frames):
            if feif_result[i]:
                rgbImgs[index]=clip[i]
                binImgs[index]=np.full((100,100), 0, dtype=np.uint8)
                thisContour = np.int32([getContour(contour[i])])
                cv2.fillPoly(binImgs[index], thisContour, (255,))
                index += 1

        #Compute the features
        
        try:
            session.putvalue('A',rgbImgs)
            session.putvalue('B',binImgs)
            session.run('C = feature_batchGenerateFeatureVector(A,B)')
            f4kfeatures = session.getvalue('C')
        except Exception:
            print("Slave {0} failed! On Task {1}!".format(name, idee))
            return (True, "FAILED", movid)
                  
        #Get Matt's features
        mattFeatures = getMattFeatures(info, clip, hasContour, contour, fish_id, print_info=False, ret_normalized_erraticity=False)

        #Normalize and transform.
        #if np.sum(feif_result) == 1:
        #    #I hate this
        #    comb = np.column_stack((f4kfeatures.reshape(1,-1), mattFeatures[feif_result]))
        #else:
        #    comb = np.column_stack((f4kfeatures, mattFeatures[feif_result]))
        #normPhi = normalizePhi(comb,self.ranges)
        #transformed_features = self.pca.transform(normPhi)
        
        np.save(savepath+".f4kfeature",f4kfeatures)
        np.save(savepath+".mattfeature",mattFeatures)
        
        #Only save 100 first feature here to save space.
        #np.save(savepath+".pcaFeature",transformed_features[:,:100])
        np.save(savepath+".feif",feif_result)
        np.save(savepath+".COMPLETE",np.array([]))
        
        #JustMatlabThings#
        del session
        sleeptime.sleep(1)
        if name[:7] == "ashbury":
            sleeptime.sleep(4)
        
        retString = "Slave: {0} completes {1} with {2} frames in {3}".format(name,idee,str(frames).ljust(6),str(datetime.now()-time))
        return (True, retString, movid)


def main():

    name = MPI.Get_processor_name()
    rank = MPI.COMM_WORLD.Get_rank()
    size = MPI.COMM_WORLD.Get_size()
    os.nice(10)

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

