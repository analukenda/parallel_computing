import multiprocessing
from random import randint
from time import sleep

# Solving N philosophers eating problem for processes
# using Ricart-Agrawala protocol and pipelines

def process_message(id,pipe,clock,responses,requests,want_to_eat):
    msg=pipe.recv()
    type = msg[0]
    id_sender = msg[1]
    t_sender = msg[2]
    print('Proces ' + str(id) + ', C=' + str(clock) + ' primio poruku ' + str(msg))
    clock = max(t_sender, clock) + 1

    if type=='z':
        if not want_to_eat[0] or (want_to_eat[0] and want_to_eat[1]>t_sender) or (want_to_eat[0] and want_to_eat[1]==t_sender and id>id_sender):
            odgovor=('o',id,t_sender)
            pipe.send(odgovor)
            print('Proces ' + str(id) + ', C=' + str(clock) + ' salje poruku ' + str(odgovor))
        else:
            requests.append((id_sender,t_sender))
    elif type=='o':
        responses.append(id_sender)
    return clock, responses, requests


def check_messages(id,pipes,clock,responses,requests,my_request):
    for pipe in pipes:
        while pipe.poll():
            clock,responses,requests=process_message(id,pipe,clock,responses,requests,my_request)
    return clock, responses, requests

def send_message(pipes, msg):
    for pipe in pipes:
        pipe.send(msg)

def philosopher(id,pipes,clock,N):
    while(True):
        print('Proces '+str(id)+' spava...')
        sleep(randint(1,7))
        want_to_eat=False
        t_mine=clock
        responses=[]
        requests=[]
        clock,responses,requests=check_messages(id,pipes,clock,responses,requests,(want_to_eat,t_mine))

        print('Proces ' + str(id) + ' zeli jesti...')
        want_to_eat=True
        t_mine=clock
        zahtjev = ('z', id, t_mine)
        print('Proces ' + str(id) + ', C=' + str(clock) + ' salje poruku ' + str(zahtjev))
        send_message(pipes,zahtjev)

        while len(responses)!=2:
            clock, responses,requests=check_messages(id,pipes, clock, responses,requests,(want_to_eat,t_mine))

        print('Proces '+str(id)+' jede...')
        sleep(randint(1,7))

        print('Proces '+str(id)+' zavrsio s jelom.')
        want_to_eat=False
        for p_waiting in requests:
            odgovor=('o',id,p_waiting[1])
            print('Proces ' + str(id) + ', C=' + str(clock) + ' salje poruku ' + str(odgovor))
            if p_waiting[0]==(id+1)%N:
                send_to_pipe=[pipes[1]]
            else:
                send_to_pipe=[pipes[0]]
            send_message(send_to_pipe,odgovor)
        clock, responses, requests = check_messages(id, pipes, clock, responses, requests, (want_to_eat, t_mine))

if __name__ == '__main__':
    N=5
    con_1,con_2=multiprocessing.Pipe()
    for i in range(N):
        try:
            con_left = con_2
            if i!=N-1:
                con_right,con_2=multiprocessing.Pipe()
            else:
                con_right=con_1
            p=multiprocessing.Process(target=philosopher,args=(i,[con_left,con_right],0,N))
            p.start()
        except KeyboardInterrupt:
            p.join()
