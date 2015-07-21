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
    max_depth = 9
    p1 = TTTMinimaxPlayer( PLAYER_X, max_depth )
    p2 = TTTRandomPlayer( PLAYER_O )
        
    g = TTTGame(p1, p2)

    b = g.GetBoard()
    b.TakeTurn(5, p1.player)
    b.TakeTurn(4, p2.player)
    
    if not g.OnePly():
        dprint(DEBUG_ERROR, "g.OnePly() faild.")
        return False
    return

if __name__ == "__main__":
    main(sys.argv)
