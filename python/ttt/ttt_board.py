import sys
sys.path.append("..")
from neat.utils import matching_import
from neat.debug import dprint
from neat import debug as debug
matching_import("DEBUG_.*", debug, globals())

PLAYER_N = "N"
PLAYER_X = "X"
PLAYER_O = "O"
PLAYER_TIE = "TIE"
LEGAL_MARKERS = (PLAYER_X, PLAYER_O)
MAX_POSITION = 8
MIN_POSITION = 0
    

class TTTBoard:

    def __init__(self):
        self.board = [ PLAYER_N for i in range(9) ]
        self.next_player = PLAYER_X
        self.winner = PLAYER_N
        return

    def GetMarker(self, position):
        if position >= MIN_POSITION and position <= MAX_POSITION:
            return self.board[position]
        else:
            dprint(DEBUG_ERROR, "Invalid position(%d)" % (position,))
            return PLAYER_N

    def GetNextPlayer(self):
        return self.next_player

    def GetWinner(self):
        return self.winner

    def OtherPlayer(self, player):
        if player not in LEGAL_MARKERS:
            dprint(DEBUG_ERROR, "Invalid player(%s)" % (player, ))
            return PLAYER_N
        if player == PLAYER_X:
            return PLAYER_O
        elif player == PLAYER_O:
            return PLAYER_X
        else:
            dprint(DEBUG_ERROR, "Invalid player(%s)" % (player, ))
            return PLAYER_N

    def TakeTurn(self, position, player):
        if position < MIN_POSITION or position > MAX_POSITION:
            dprint(DEBUG_ERROR, "Invalid position(%d)" % (position, ))
            return False
        if player not in LEGAL_MARKERS:
            dprint(DEBUG_ERROR, "Invalid player(%s)" % (player, ))
            return False
        if self.board[position] != PLAYER_N:
            dprint(DEBUG_ERROR, "Position(%d) already played = %s" % (position, player))
            return False
        if self.next_player != player:
            dprint(DEBUG_ERROR, "Invalid next player(%s), should be (%s)." % (player, self.next_player))
            return False
            
        self.board[position] = player;
        self.next_player = self.OtherPlayer(player)

        self.CheckWin()
        
        return True

    def CheckWin(self):
        wins = [ ( 0, 1, 2 ), ( 3, 4, 5 ), ( 6, 7, 8 ),
                 ( 0, 3, 6 ), ( 1, 4, 7 ), ( 2, 5, 8 ),
                 ( 0, 4, 8 ), ( 2, 4, 6 ) ]
        for w in wins:
            if self.board[w[0]] != PLAYER_N and self.board[w[0]] == self.board[w[1]] and self.board[w[0]] == self.board[w[2]]:
                self.winner = self.board[w[0]]
                return True
        return False

    def Display(self):
        s = "+---+---+---+\n"
        for row in range(3):
            s += "|"
            for col in range(3):
                m = self.board[row*3+col]
                if m == PLAYER_N:
                    m = " "
                s += " %s |" % (m, )
            s += "\n+---+---+---+\n"
        print s
        return

        
        
        
def main():
    b = TTTBoard()
    b.TakeTurn(4, PLAYER_X)
    b.TakeTurn(0, PLAYER_O)
    b.TakeTurn(1, PLAYER_X)
    b.Display()
    return

if __name__ == "__main__":
    main()

