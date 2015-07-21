import sys
sys.path.append("..")
from neat.utils import matching_import
from neat.debug import dprint
from neat import debug as debug
matching_import("DEBUG_.*", debug, globals())

from ttt_board import *
from ttt_random_player import TTTRandomPlayer

class TTTGame:

    def __init__(self, player_x, player_o):
        self.board = TTTBoard()
        self.player_x = player_x
        self.player_o = player_o
        return

    def GameIsOver(self):
        return self.board.GetWinner() != PLAYER_N

    def OnePly(self):
        if self.GameIsOver():
            return False
        tmp_board = self.board.copy()
        tmp_player = self.board.GetNextPlayer()
        if tmp_player == PLAYER_X:
            m = self.player_x.ChooseMove(tmp_board)
        elif tmp_player == PLAYER_O:
            m = self.player_o.ChooseMove(tmp_board)
        else:
            dprint(DEBUG_ERROR, "Unexpected self.board.next_player = %s." % (tmp_player, ))
            m = None
            return False

        if self.board.GetMarker(m) != PLAYER_N:
            # bad move, just count as a ply, don't try it
            return True
            
        if not self.board.TakeTurn(m, tmp_player):
            dprint(DEBUG_ERROR, "self.board.TakeTurn(%d, %s) failed." % (m, tmp_player))
            if debug.is_set(DEBUG_ERROR):
                if tmp_player == PLAYER_X:
                    curplayer = self.player_x
                elif tmp_player == PLAYER_O:
                    curplayer = self.player_o
                dprint(DEBUG_ERROR, "%s chose %d." % (curplayer.__class__.__name__, m))

            return False
            
        return True


    def GameLoop(self):
        max_ply = 10
        cur_ply = 1
        while (not self.GameIsOver()) and (cur_ply <= max_ply):
            if not self.OnePly():
                dprint(DEBUG_ERROR, "OnePly failed.")
                return False
            cur_ply += 1

        return True
            
    def GetBoard(self):
        return self.board


def main():
    p1 = TTTRandomPlayer( PLAYER_X )
    p2 = TTTRandomPlayer( PLAYER_O )
    g = TTTGame(p1, p2)
    if not g.GameLoop():
        dprint(DEBUG_ERROR, "g.GameLoop() failed.")
        return False
    b = g.GetBoard()
    b.Display()
    print "Winner is: %s." % (b.GetWinner(), )
    return

if __name__ == "__main__":
    main()
