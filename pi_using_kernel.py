import math
import time
import numpy
import pyopencl

N=int(input('Upisite N: '))
M=input('Upisite M(ako zelite): ')
if M.strip()!='':
    M=int(M)
    if M<N:
        L=input('Upisite L(ako zelite): ')
        if L.strip()!='':
            L=int(L)
            if L>int(N/M) or int(N/M)%L!=0:
                L=None
            else:
                L=(L,)
        else:
            L=None
    else:
        M=N
        L=None
else:
    M=N
    L=None

if M==N:
    start=time.time()
    rez=[]
    h=1.0/N
    for i in range(1,N+1):
        rez.append((4.0*h)*(1/(1.0+math.pow(h*(i-0.5),2))))
else:
    kontekst=pyopencl.create_some_context()
    start=time.time()
    rez=numpy.array([0.0 for i in range(N)]).astype(numpy.float64)
    rez_g=pyopencl.Buffer(kontekst,pyopencl.mem_flags.WRITE_ONLY,rez.nbytes)

    paralelni=pyopencl.Program(kontekst,"""
        __kernel void pi(__global double* rez,const int N){
            double h=1.0/N;
            double suma=0.0; 
            int M=N/get_global_size(0); 
            int index_begin=(get_global_id(0)*M)+1;
            int index_end=index_begin+M;
            if (index_end>N+1){
                index_end=N+1;
                }       
            for(int i=index_begin;i<index_end;++i){
                suma+=4.0/(1.0+pow(h*((double)i-0.5),2));
            }
            rez[get_global_id(0)]=h*suma;
        }
        """)

    naredbe=pyopencl.CommandQueue(kontekst)
    paralelni.build().pi(naredbe,(int(N/M),),L,rez_g,numpy.int32(N))
    pyopencl.enqueue_copy(naredbe,rez,rez_g)

pi=0.0
for i in rez:
    pi+=i
end=time.time()
print('Pi: ',str(pi))
print('Trajanje: '+str(end-start)+' sekundi')
