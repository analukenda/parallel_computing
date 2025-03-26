import math
import time
from sys import argv

import numpy
import pyopencl

def boundarypsi(psi,m,n,b,h,w):
    for i in range(b+1,b+w):
        psi[i][0]=i-b
    for i in range(b+w,m+1):
        psi[i][0]=w
    for j in range(1,h+1):
        psi[m+1][j]=w
    for j in range(h+1,h+w):
        psi[m+1][j]=w-1+h

printfreq = 100
error = None
tolerance = 0.0
bbase = 10
hbase = 15
wbase = 5
mbase = 32
nbase = 32
irrotational = 1
checker = 0
if tolerance > 0:
    checker = 1

if len(argv) != 3:
    print('Usage: python zad3.py <scale> <numiter>')
    exit(1)
scalefactor = int(argv[1])
numiter = int(argv[2])
if checker == 0:
    print('Scale Factor = ' + str(scalefactor) + ', iterations = ' + str(numiter))
else:
    print('Scale Factor = ' + str(scalefactor) + ', iterations = ' + str(numiter) + ', tolerance = ' + str(tolerance))
print('Irrotational flow!')

b = bbase * scalefactor
h = hbase * scalefactor
w = wbase * scalefactor
m = mbase * scalefactor
n = nbase * scalefactor
print('Running CFD on ' + str(m) + ' x ' + str(n) + ' grid in serial')

psi = numpy.zeros((m + 2, n + 2))
psitmp = numpy.zeros((m + 2, n + 2))

kontekst = pyopencl.create_some_context()
naredbe = pyopencl.CommandQueue(kontekst)
paralelni = pyopencl.Program(kontekst, """
     __kernel void jacobistep(__global double *psitmp,__global const double *psi,const int m,const int n) {
        int i=get_global_id(0)+1;
        int j=get_global_id(1)+1;
        if (i<m+1 && j <n+1){
            psitmp[i*(m+2)+j]=0.25*(psi[(i-1)*(m+2)+j]+psi[(i+1)*(m+2)+j]+psi[i*(m+2)+j-1]+psi[i*(m+2)+j+1]);
        }
    }

    __kernel void copy_back(__global const double *psitmp, __global double *psi,const int m,const int n){
        int i=get_global_id(0)+1;
        int j=get_global_id(1)+1;
        psi[i*(m+2)+j]=psitmp[i*(m+2)+j];
    }

""").build()


psitmp_g = pyopencl.Buffer(kontekst, pyopencl.mem_flags.WRITE_ONLY, psitmp.nbytes)
boundarypsi(psi,m,n,b,h,w)
psi_g = pyopencl.Buffer(kontekst, pyopencl.mem_flags.READ_ONLY | pyopencl.mem_flags.COPY_HOST_PTR, hostbuf=psi)

bnorm = 0.0
for i in range(m + 2):
    for j in range(n + 2):
        bnorm += math.pow(psi[i][j], 2)
bnorm = math.sqrt(bnorm)
print()
print('Starting main loop...')
print()
start = time.time()
iter = 0

for i in range(1, numiter + 1):
    iter = i
    paralelni.jacobistep(naredbe, (m, n), None, psitmp_g, psi_g, numpy.int32(m), numpy.int32(n))
    if checker == 1 or i == numiter:
        pyopencl.enqueue_copy(naredbe, psi, psi_g)
        pyopencl.enqueue_copy(naredbe, psitmp, psitmp_g)
        error = 0.0
        for j in range(1, m + 1):
            for k in range(1, n + 1):
                error += math.pow(psitmp[j][k] - psi[j][k], 2)
        error = math.sqrt(error)
        error = error / bnorm
    if checker == 1:
        if error < tolerance:
            print('Converged on iteration ' + str(i))
            break
    paralelni.copy_back(naredbe, (m, n), None, psitmp_g, psi_g, numpy.int32(m), numpy.int32(n))
    if i % printfreq == 0:
        if checker == 0:
            print('Completed iteration ' + str(i))
        else:
            print('Completed iteration ' + str(i) + ', error ' + str(error))

if iter > numiter:
    iter = numiter
end = time.time()
ttot = end - start
titer = ttot / iter
print()
print('...finished')
print('After ' + str(iter) + ' iterations, the error is ' + str(error))
print('Time for ' + str(iter) + ' iterations was ' + str(ttot) + ' seconds')
print('Each iteration took ' + str(titer) + ' seconds')
print('...finished')



