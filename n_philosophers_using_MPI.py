import random
import time
import numpy
from mpi4py import MPI

class Fork():
    def __init__(self,dirty):
        self.dirty=dirty

comm=MPI.COMM_WORLD
rank=comm.Get_rank()
size=comm.Get_size()

requests=[False,False]
indexes=[(rank-1)%size,(rank+1)%size]
tag_request=1
tag_fork=2
sides=[0,1]
forks=[None,None]

if rank!=size-1:
    forks[1]=Fork(True)
if rank==0:
    forks[0]=Fork(True)

def free_fork(side):
    comm.Send(buf=[numpy.array([1]), MPI.INT], dest=indexes[side], tag=tag_fork)
    forks[side] = None
    requests[side] = False

def check_requests():
    for side in sides:
        if comm.Iprobe(source=indexes[side],tag=tag_request):
            comm.Recv(buf=[numpy.array([1]),MPI.INT],source=indexes[side],tag=tag_request)
            requests[side]=True
    for side in sides:
        if requests[side]:
            if forks[side] is not None and forks[side].dirty:
                free_fork(side)

def output(action):
    print('    '*rank+action,flush=True)

while True:
    output('mislim')
    for i in range(random.randint(1,5)):
        time.sleep(1)
        check_requests()

    output('trazim vilicu ('+str(rank)+')')
    while forks[0] is None or forks[1] is None:
        for side in sides:
            if forks[side] is None:
                comm.Send(buf=[numpy.array([1]),MPI.INT],dest=indexes[side],tag=tag_request)
                while forks[side] is None:
                    if comm.Iprobe(source=indexes[side],tag=tag_fork):
                        comm.Recv(buf=[numpy.array([1]),MPI.INT],source=indexes[side],tag=tag_fork)
                        forks[side]=Fork(False)
                    check_requests()

    output('jedem')
    time.sleep(random.randint(1,5))
    for side in sides:
        if not forks[side].dirty:
            forks[side].dirty=True
    check_requests()