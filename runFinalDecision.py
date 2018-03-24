#!/afs/inf.ed.ac.uk/user/s14/s1413557/miniconda2/bin/python

from __future__ import print_function

from mpi4py import MPI
from mpi.master_slave import Master, Slave
from mpi.work_queue import WorkQueue
from datetime import datetime
from f4klib import loadMovids, loadLengths
import os
import multiprocessing
import time as sleeptime
import numpy as np

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
        
        start = 0
        end = 396901
        
        #Put longer task at start.
        if end == 396901:
            order = np.argsort(movs_length[start:])
        else:
            order = np.argsort(movs_length[start:end])
        
        #For statistics
        totWork = 0
        completed = 0
        
        print("Master loading work queue.")
        for i in np.arange(start,end)[order]:
               
            totWork += 1
            movid = movs[i]
            self.work_queue.add_work(data=('Do stuff', movid))
        
        print("Master loading work queue done.")
        
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
    
    savepath = "/afs/inf.ed.ac.uk/group/project/F4KC/final/{0}/{1}/{2}".format(idee[0],idee[0:2],idee)

    #Check if video is already extracted.
    if os.path.isfile(savepath+".COMPLETE.npy"):
        q.put([True, 'Slave: %s skipped   %s because it\'s done.' % (name, idee), movid])
        return

    #Load the video
    time = datetime.now()
    try:
        savepath2 = "/afs/inf.ed.ac.uk/group/project/F4KC/output/{0}/{1}/{2}"
        result = np.load(savepath2.format(idee[0],idee[0:2],idee)+".YHAT.npy")
    except IOError:
        #Skipping empty videos
        np.save(savepath+".COMPLETE",np.array([]))
        q.put([True, 'Slave: %s skipped   %s because it\'s empty' % (name, idee), movid])
        return
    
    # ==================== PROCESSING ====================
     
    answer = result[:,0,5] > 0.01081
    
    np.save(savepath+".RESULT",answer)
    np.save(savepath+".COMPLETE",np.array([]))
    
    frames = len(answer)

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

