import sys
sys.path.append("..")
from neat.utils import matching_import
from neat.debug import dprint
from neat import debug as debug
matching_import("DEBUG_.*", debug, globals())

import random

from ttt_game import TTTGame
from ttt_board import *
from ttt_random_player import TTTRandomPlayer
from ttt_human_player import TTTHumanPlayer
from ttt_minimax_player import TTTMinimaxPlayer

def main(argv):
    max_depth = 1
    if len(argv) > 1:
        max_depth = int(argv[1])
                
    if random.random() < 0.5:
        p1 = TTTRandomPlayer( PLAYER_X )
        p2 = TTTMinimaxPlayer( PLAYER_O, max_depth )
        #p2 = TTTHumanPlayer( PLAYER_O )
    else:
        #p1 = TTTHumanPlayer( PLAYER_X )
        p1 = TTTMinimaxPlayer( PLAYER_X, max_depth )
        p2 = TTTRandomPlayer( PLAYER_O )
        
    g = TTTGame(p1, p2)
    if not g.GameLoop():
        dprint(DEBUG_ERROR, "g.GameLoop() faild.")
        return False
    b = g.GetBoard()
    b.Display()
    if b.GetWinner() == PLAYER_X:
        print "Winner is %s." % (p1.__class__.__name__, )
    elif b.GetWinner() == PLAYER_O:
        print "Winner is %s." % (p2.__class__.__name__, )
    else:
        print "Winner is %s." % (b.GetWinner(), )
    return

if __name__ == "__main__":
    main(sys.argv)
