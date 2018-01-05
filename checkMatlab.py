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
        
        for i in np.arange(MPI.COMM_WORLD.Get_size()-1):
            self.work_queue.add_work(data=('Do stuff', i))

       
        while not self.work_queue.done():

            self.work_queue.do_work()

            #
            # reclaim returned data from completed slaves
            #
            for slave_return_data in self.work_queue.get_completed_work():
                done, message = slave_return_data
                if done:
                    print("Slave {0} is clear".format(message))

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
        name = MPI.Get_processor_name().ljust(30)
        task, _ = data
        
        try:
            session = pymatlab.session_factory('matlab -nodisplay')
            session.run("addpath('/afs/inf.ed.ac.uk/user/s14/s1413557/f4k-2017-msc-master/matt-msc/workspace/f4k/fish_recog')")
            if name[:7] == "ashbury":
                #Our HERO, the MAGNIFICENT and MOST EDUCATIONAL sir ASHBURY, the ONE with FORTY EXTRAVAGANZA PROCESSORS.
                print("ACTIVATE SPELL CARD: POOL40!")
                session.run("pc = parcluster('local')")
                session.run('pc.NumWorkers = 40')
                session.run('parpool(40)')
                #Perhaps people working on it wont hate me.
        except Exception:
            print('Slave: %s crashed!' % (name))
        
        del session
        
        return (True, name)


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

