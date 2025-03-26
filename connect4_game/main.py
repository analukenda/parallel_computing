import time
import math
from random import randint
from sys import argv
from mpi4py import MPI
import play
from itertools import product
world=MPI.COMM_WORLD
size=world.Get_size()
rank=world.Get_rank()
tag_req=1
tag_resp=2
tag_result=3
tag_break=4
if len(argv)<=1:
    search_depth=7
else:
    search_depth=int(argv[1])
master_depth=int(math.ceil(math.log(search_depth * size, 7)))

def subtree(d,player,new_game):
    end=new_game.end_check()
    if end:
        if end==play.computer:
            return 1
        elif end==play.person:
            return -1
        else:
            return 0
    if d==0:
        return 0
    overall_score=0.0
    moves_made=0
    current_player=play.next_on_move(player)
    for move in new_game.possible_moves():
        new_game.move(current_player,move)
        moves_made+=1
        score=subtree(d-1,current_player,new_game)
        new_game.undo()
        if score==1 and current_player==play.computer:
            return 1
        if score==-1 and current_player==play.person:
            return -1
        overall_score+=score
    return overall_score/moves_made

def single_process_decision(new_game):
    player=play.computer
    d=search_depth
    best=-1
    column=-1
    while d>0 and best==-1:
        best_column=-1
        for move in new_game.possible_moves():
            if best_column==-1:
                best_column=move
            new_game.move(player,move)
            score=subtree(d-1,player,new_game)
            new_game.undo()
            if score>best or (score==best and randint(1,2)==1):
                best_column=move
                best=score
        column=best_column
        d//=2
    return column

def multiple_process_decision(new_game):
    scores = {}
    moves = list(map(list, list(product([x for x in range(new_game.width)], repeat=master_depth))))
    moves=[]
    for i in range(new_game.width):
        for j in range(new_game.width):
            moves.append((i,j))
    while len(moves) > 0:
        status = MPI.Status()
        world.iprobe(status=status)
        if status.Get_tag() == tag_result:
            result = world.recv(source=status.Get_source(),tag=tag_result)
            if result is not None:
                scores[tuple(result[0])] = result[1]
        if status.Get_tag() == tag_req:
            world.recv(source=status.Get_source(),tag=tag_req)
            world.send(obj=(new_game.previous_columns(),moves.pop()),dest=status.Get_source(),tag=tag_resp)
    final=[]
    for i in range(new_game.width):
        final.append([0.0,0])
    for score in scores:
        final[score[0]][0] += scores[score]
        final[score[0]][1]+=1
    best_move=max(enumerate(final), key=lambda x: x[1])[0]
    return best_move

def loop(decision_function,player,new_game):
    new_game.field_print()
    while(True):
        if player==play.computer:
            start=time.time()
            column=decision_function(new_game)
            end=time.time()
            print('Racunalo je odabralo stupac '+str(column)+' u '+str(end-start)+' sekundi.')
        else:
            column=int(input('Upisite stupac u koji zelite ubaciti novcic: '))
            while new_game.impossible_move(column):
                column = int(input('Neispravan stupac. Pokusajte ponovno: '))
        new_game.move(player,column)
        new_game.field_print()
        player=play.next_on_move(player)
        winner=new_game.end_check()
        if winner:
            print('--------------------------------------------')
            if winner==play.none:
                print('Igra je zavrsila bez pobjednika.')
            else:
                print('Igrac '+winner+' je pobijedio!')
            break

new_game=play.Play()
player=play.person
if size==1:
    loop(single_process_decision,player,new_game)
else:
    while True:
        if rank!=0:
            world.send(obj=None, dest=0, tag=tag_req)
            status = MPI.Status()
            while not world.iprobe(source=0, tag=MPI.ANY_TAG, status=status):
                continue
            tag = status.Get_tag()
            if tag == tag_break:
                world.recv(source=0, tag=tag)
                break
            elif tag == tag_resp:
                new_game = play.Play()
                past, future = world.recv(source=0, tag=tag)
                for move in past:
                    new_game.move(player, move)
                    player = play.next_on_move(player)
                valid_moves = True
                for move in future:
                    if new_game.impossible_move(move):
                        valid_moves = False
                        break
                    new_game.move(player, move)
                    player = play.next_on_move(player)
                if valid_moves:
                    world.send(obj=(future, subtree(search_depth-master_depth, player, new_game)), dest=0, tag=tag_result)

                else:
                    world.send(obj=None, dest=0, tag=tag_result)
        else:
            loop(multiple_process_decision,player,new_game)
            for i in range(1, size):
                world.send(obj=None,dest=i,tag=tag_break)
