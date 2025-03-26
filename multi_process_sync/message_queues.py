import multiprocessing
from random import randint
from time import sleep
from queue import Empty

# Solving N philosophers eating problem for processes
# using Lamport protocol and message queues

def process_message(msg,id,queues,clock,responses,q_internal):
    type=msg[0]
    id_sender=msg[1]
    t_sender=msg[2]
    print('Proces '+str(id)+', C='+str(clock)+' primio poruku '+str(msg))
    clock = max(t_sender, clock) + 1

    if type=='z':
        q_internal.append((id_sender,t_sender))
        q_internal=sorted(q_internal,key=lambda x:(x[1],x[0]))
        odgovor=('o',id_sender,clock)
        print('Proces ' + str(id) + ', C=' + str(clock) + ' salje poruku ' + str(odgovor))
        queues[id_sender].put(odgovor)
    elif type=='o':
        responses.append((id_sender,t_sender))
    elif type=='i':
        q_internal.remove((id_sender,t_sender))
    return clock, responses, q_internal

def check_messages(id,queues,clock,responses,q_internal):
    while(True):
        try:
            msg=queues[id].get(block=False)
            clock, responses, q_internal=process_message(msg,id, queues, clock, responses,q_internal)
        except Empty:
            return clock,responses, q_internal

def send_message(id_reciever,queues,msg):
    queues[id_reciever].put(msg)

def philosopher(id,queues,clock,N):
    q_internal=[]
    while(True):
        print('Proces '+str(id)+' spava...')
        sleep(randint(1,7))
        responses=[]
        clock,responses,q_internal=check_messages(id,queues,clock,responses,q_internal)

        print('Proces '+str(id)+' zeli jesti...')
        q_internal.append((id,clock))
        q_internal=sorted(q_internal,key=lambda x:(x[1],x[0]))
        Ti=clock
        zahtjev=('z',id,Ti)
        print('Proces '+str(id)+', C='+str(clock)+' salje poruku '+str(zahtjev))
        for id_reciever in [id-1,(id+1)%N]:
            send_message(id_reciever,queues,zahtjev)
        while len(responses)!=2 or q_internal[0][0]!=id:
            clock, responses,q_internal=check_messages(id,queues, clock, responses,q_internal)

        print('Proces '+str(id)+' jede...')
        sleep(randint(1,7))

        print('Proces '+str(id)+' zavrsio s jelom.')
        q_internal.pop(0)
        izlazak=('i',id,Ti)
        print('Proces '+str(id)+', C='+str(clock)+' salje poruku '+str(izlazak))
        for id_reciever in [id-1,(id+1)%N]:
            send_message(id_reciever,queues,izlazak)
        clock, responses, q_internal = check_messages(id, queues, clock, responses, q_internal)

if __name__ == '__main__':
    N=5
    q = []
    for i in range(N):
        q.append(multiprocessing.Queue())
    for i in range(N):
        try:
            p=multiprocessing.Process(target=philosopher,args=(i,q,0,N))
            p.start()
        except KeyboardInterrupt:
            p.join()