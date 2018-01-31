#!/afs/inf.ed.ac.uk/user/s14/s1413557/miniconda2/bin/python

from __future__ import print_function

import time as sleeptime
from mpi4py import MPI
from mpi.master_slave import Master, Slave
from mpi.work_queue import WorkQueue
from f4klib import *


from sklearn.model_selection import KFold
from sklearn.svm import SVC

from enum import IntEnum

# Define MPI message tags
Tags = IntEnum('Tags', 'READY START DONE EXIT')

#HOSTS=basso,battaglin,belloni,bergamaschi,berrendero,bertoglio,berzin,binda
#mpiexec -n 104 -host $HOSTS python ~/f4k/runMulticoreSVMTest.py

folds = 10

gammas = 1
#ls = np.logspace(-2,0,gammas)
#ls = np.linspace(0.1,0.3,gammas)
ls = np.linspace(0.1,0.1,gammas)

cs = 1
#ls2 = np.logspace(-2,3,cs) #High C -> hours of train time.
#ls2 = np.linspace(2,20,cs)
ls2 = np.linspace(10,10,cs)

pcs = 11
ls3 = np.linspace(30,40,pcs)


class MyApp(object):

    def __init__(self, slaves):
        self.master = Master(slaves)
        self.work_queue = WorkQueue(self.master)

    def terminate_slaves(self):
        self.master.terminate_slaves()

    def run(self):
        
        time = datetime.now()
        
        totWork = 0#end - start
        completed = 0
        
        for i in np.arange(folds): #Fold
            for j in np.arange(gammas): #Gamma
                for k in np.arange(cs): #C
                    for n in np.arange(pcs):
                        totWork += 1
                        self.work_queue.add_work(data=('Do stuff', i, j, k, n))
                
        scores = np.zeros((folds,gammas,cs,pcs))

                
        #for i in range(tasks):
        #    self.work_queue.add_work(data=('Do stuff', i))
       
        while not self.work_queue.done():

            self.work_queue.do_work()

            #
            # reclaim returned data from completed slaves
            #
            for slave_return_data in self.work_queue.get_completed_work():
                done, message, i, j, k, n, score = slave_return_data
                if done:
                    completed += 1
                    scores[i,j,k,n] = score
                    print("Progress: {0}/{1}, took {2}. {3}"
                      .format(str(completed).rjust(6),str(totWork).rjust(6),str(datetime.now()-time),message))

            # sleep some time
            sleeptime.sleep(0.001)
        np.save("/afs/inf.ed.ac.uk/group/ug4-projects/s1413557/training/svmscore/scores", scores)

class MySlave(Slave):
    """
    A slave process extends Slave class, overrides the 'do_work' method
    and calls 'Slave.run'. The Master will do the rest
    """

    def __init__(self):
        
        super(MySlave, self).__init__()
        self.features, self.targets = loadTrainDataSet()
        self.X = self.features[:,:30]
        self.y = self.targets[:].astype('int') 
           
    def run(self):
        """
        Invoke this method when ready to put this slave to work
        """
        status = MPI.Status()
        
        while True:
            self.comm.send(None, dest=0, tag=Tags.READY)
            data = self.comm.recv(source=0, tag=MPI.ANY_TAG, status=status)
            tag = status.Get_tag()
            sleeptime.sleep(1)
    
            if tag == Tags.START:
                # Do the work here
                result = self.do_work(data)
                self.comm.send(result, dest=0, tag=Tags.DONE)
            elif tag == Tags.EXIT:
                break
        
        self.comm.send(None, dest=0, tag=Tags.EXIT)
            
    def do_work(self, data):
        name = MPI.Get_processor_name().split(".")[0].ljust(12)
        task, fold, gamma, c, pc = data
        time = datetime.now()
        
        print('                                              Slave: {0} started   fold {1}, gamma {2:.4g}, C {3:.4g}, {4}pcs'
          .format(name, fold+1, ls[gamma], ls2[c], int(ls3[pc])))
        
        features,targets = loadTrainDataSet()
        kf = KFold(n_splits=folds, random_state=420, shuffle=True)
        
        counter = 0
        for train_index, test_index in kf.split(X=self.X[:,:int(ls3[pc])], y=self.y):
            if  str(counter) != str(fold):
                counter += 1
                continue
            #print("TRAIN:", train_index, "TEST:", test_index)
            X_train, X_test = self.X[:,:int(ls3[pc])][train_index], self.X[:,:int(ls3[pc])][test_index]
            y_train, y_test = self.y[train_index], self.y[test_index]
            svc = SVC(kernel='rbf',gamma=ls[gamma],C=ls2[c])
            svc.fit(X_train,y_train)
            score = svc.score(X_test,y_test)
            retString = "Slave: {0} completes fold {1}, gamma {2:.4g}, C {3:.4g}, {4}pcs in {5}"
            retString = retString.format(name, fold+1, ls[gamma], ls2[c], int(ls3[pc]), str(datetime.now()-time))
            return (True, retString, fold, gamma, c, pc, score)
        
        print("RETURNED WRONG")
        return (False, "", 0, 0, 0, 0, 0)
                
    
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

