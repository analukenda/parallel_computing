import random
from sys import argv
import numpy
import pyopencl

N=int(argv[1])
if len(argv)>2:
    M=int(argv[2])
else:
    M=N
X=numpy.array([random.random() for i in range(N)]).astype(numpy.float32)
Y=numpy.array([random.random() for i in range(N)]).astype(numpy.float32)
prosjeci=numpy.array([0.0 for i in range(N)]).astype(numpy.float32)
kontekst=pyopencl.create_some_context()

paralelni=pyopencl.Program(kontekst,""" 
	__kernel void udaljenost(const __global float* X,const __global float* Y,__global float* prosjeci,const int N){
        for (int i=get_global_id(0);i<N;i+=get_global_size(0)){
            float suma=0.0f;
            for (int j=0;j<N;++j){
                suma+=sqrt(pow(X[j]-X[i],2)+pow(Y[j]-Y[i],2));
            }
            prosjeci[i]=suma/(N-1);
        }
    }
    """)

X_g=pyopencl.Buffer(kontekst,pyopencl.mem_flags.READ_ONLY | pyopencl.mem_flags.COPY_HOST_PTR,hostbuf=X)
Y_g=pyopencl.Buffer(kontekst,pyopencl.mem_flags.READ_ONLY | pyopencl.mem_flags.COPY_HOST_PTR,hostbuf=Y)
prosjeci_g=pyopencl.Buffer(kontekst,pyopencl.mem_flags.WRITE_ONLY,prosjeci.nbytes)
naredbe=pyopencl.CommandQueue(kontekst)
paralelni.build().udaljenost(naredbe,(int(N/M),),None,X_g,Y_g,prosjeci_g,numpy.int32(N))
pyopencl.enqueue_copy(naredbe,prosjeci,prosjeci_g)

prosjek=0.0
for grad in prosjeci:
    prosjek+=grad
prosjek/=N
print('Prosjecna udaljenost: ',str(prosjek))
