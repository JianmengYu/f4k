#!/afs/inf.ed.ac.uk/user/s14/s1413557/miniconda2/bin/python

from __future__ import print_function

import time as sleeptime
from mpi4py import MPI
from mpi.master_slave import Master, Slave
from mpi.work_queue import WorkQueue
from f4klib import *


#HOSTS=basso,battaglin,belloni,bergamaschi,berrendero,bertoglio,berzin,binda
#export HOSTS
#echo $HOSTS
#mpiexec -n 8 -host $HOSTS python ~/f4k/runMulticoreFeatureExtract.py


class MyApp(object):

    def __init__(self, slaves):
        self.master = Master(slaves)
        self.work_queue = WorkQueue(self.master)

    def terminate_slaves(self):
        self.master.terminate_slaves()

    def run(self):
        
        time = datetime.now()
        
        movs = loadMovids()
        #13b: np.arange(30598,30695)
        totWork = 30695 - 30598
        completed = 0
        
        for i in np.arange(30598,30695):
            movid = movs[i]
            self.work_queue.add_work(data=('Do stuff', movid))

                
        #for i in range(tasks):
        #    self.work_queue.add_work(data=('Do stuff', i))
       
        while not self.work_queue.done():

            self.work_queue.do_work()

            #
            # reclaim returned data from completed slaves
            #
            for slave_return_data in self.work_queue.get_completed_work():
                done, message = slave_return_data
                if done:
                    completed += 1
                    print("Progress: {0}/{1}, took {2}. {3}"
                          .format(str(completed).rjust(6),str(totWork).rjust(6),str(datetime.now()-time),message))

            # sleep some time
            sleeptime.sleep(0.3)

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
        
        time = datetime.now()
        
        info, clip, hasContour, contour, fish_id, frames = loadVideo(movid)
        idee = movid[0]
        fname = movid[0].split("#")[0]
        
        if frames == 0:
            #Skipping stuff
            #print('Slave: %s skipped an empty video "%s"' % (name, idee))
            return (True, 'Slave: %s skipped   %s' % (name, idee))
        
        session = pymatlab.session_factory('matlab -nojvm -nodisplay')
        session.run("addpath('/afs/inf.ed.ac.uk/user/s14/s1413557/f4k-2017-msc-master/matt-msc/workspace/f4k/fish_recog')")

        f4kfeatures = np.zeros((frames,2626))
        feif_result = np.zeros(frames, dtype=bool)
        
        print('                                              Slave: {0} started   {1} with {2} frames'
              .format(name, idee, str(frames).ljust(6)))
        if movid[2] == "1":
            frame_size = "640x480"
        else:
            frame_size = "320x240"

        for i in range(frames):
            if hasContour[i]:
                if not FEIF(contour[i], frame_size, matt_mode=True):
                    feif_result[i] = True
                    thisContour = np.int32([getContour(contour[i])])
                    image = clip[i]
                    full_fish = np.full((100,100), 0, dtype=np.uint8)
                    cv2.fillPoly(full_fish, thisContour, (255,))
                    session.putvalue('A',image)
                    session.putvalue('B',full_fish)
                    session.run('C = feature_generateFeatureVector(A,B,false);')
                    f4kfeatures[i,:] = session.getvalue('C')

        mattFeatures = getMattFeatures(info, clip, hasContour, contour, fish_id, print_info=False, ret_normalized_erraticity=False)

        savepath = "/afs/inf.ed.ac.uk/group/ug4-projects/s1413557/features/{0}/{1}/{2}".format(idee[0],idee[0:2],idee)
        np.save(savepath+".f4kfeature",f4kfeatures)
        np.save(savepath+".mattfeature",mattFeatures)
        np.save(savepath+".feif",feif_result)
        
        del session
        
        retString = "Slave: {0} completes {1} with {2} frames in {3}".format(name,idee,str(frames).ljust(6),str(datetime.now()-time))
        return (True, retString)


def main():

    name = MPI.Get_processor_name()
    rank = MPI.COMM_WORLD.Get_rank()
    size = MPI.COMM_WORLD.Get_size()

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

