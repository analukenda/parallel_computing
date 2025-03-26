win=4
person='A'
computer='C'
none='-'

def substract(elements):
    return elements[0]-elements[1]

def next_on_move(player):
    if player==person:
        return computer
    else:
        return person

class Play:
    def __init__(self, height=6, width=7):
        self.height=height
        self.width=width
        self.field=[]
        self.previous_moves=[]

        for i in range(width):
            column=[]
            for j in range(height):
                column.append(none)
            self.field.append(column)

    def column_out_of_range(self,column):
        if column<0 or column>=self.width:
            return True
        return False

    def row_out_of_range(self,row):
        if row<0 or row>=self.height:
            return True
        return False

    def impossible_move(self,column):
        if self.column_out_of_range(column) or self.field[column][self.height-1]!=none:
            return True
        return False

    def possible_moves(self):
        moves=[]
        for i in range(self.width):
            if not self.impossible_move(i):
                moves.append(i)
        return moves

    def previous_columns(self):
        columns=[]
        for move in self.previous_moves:
            columns.append(move[1])
        return columns

    def move(self,player,column):
        if not self.impossible_move(column):
            for i in range(self.height):
                if self.field[column][i]==none:
                    self.field[column][i]=player
                    self.previous_moves.append((player,column,i))

                    break

    def undo(self):
        last_move=self.previous_moves.pop()
        self.field[last_move[1]][last_move[2]]=none

    def check_win_streak(self,states,player):
        streak=0
        for state in states:
            if state==player:
                streak+=1
                if streak==win:
                    return True
            else:
                streak=0
        return False

    def check_diagonal(self,column,row,player,side):
        if side=='left':
            oper_left=substract
            oper_right=sum
        else:
            oper_left=sum
            oper_right=substract
        around_states=[]
        for i in range(win-1,0,-1):
            current_column=column-i
            if not self.column_out_of_range(current_column):
                current_row=oper_left([row,i])
                if not self.row_out_of_range(current_row):
                    around_states.append(self.field[current_column][current_row])
        around_states.append(player)
        for i in range(1,win):
            current_column=column+i
            if not self.column_out_of_range(current_column):
                current_row=oper_right([row,i])
                if not self.row_out_of_range(current_row):
                    around_states.append(self.field[current_column][current_row])
        return around_states

    def end_check(self):
        last_move=self.previous_moves[-1]
        player=last_move[0]
        column=last_move[1]
        row=last_move[2]

        if row>=win-1:
            for i in range(1,win):
                if self.field[column][row-i]==player:
                    if i==win-1:
                        return player
                else:
                    break

        around_states=[]
        for i in range(column-(win-1),column+win):
            if not self.column_out_of_range(i):
                around_states.append(self.field[i][row])
        if self.check_win_streak(around_states,player):
            return player

        around_states=self.check_diagonal(column,row,player,'left')
        if self.check_win_streak(around_states,player):
            return player

        around_states = self.check_diagonal(column,row,player,'right')
        if self.check_win_streak(around_states, player):
            return player

        if len(self.possible_moves())==0:
            return none

        return False

    def field_print(self):
        for i in range(self.height-1,-1,-1):
            s=''
            for j in range(self.width):
                s+=self.field[j][i]+'    '
            print(s)
            print()