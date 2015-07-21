import sys, getopt
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
from ttt_genome_player import TTTGenomePlayer


def usage():
    print "usage: %s --player1 (rhmg) [ --level1 (1-9) ] [ --genome1 (filename) ] --player2 (rhmg)  [ --level1 (1-9) ] [ --genome1 (filename) ]" % (sys.argv[0])
    print "-p|--player1     : player 1 type Random Human Minimax Genome"
    print "-P|--player2     : player 2 type Random Human Minimax Genome"
    print "-l|--level1      : player 1 minimax depth"
    print "-L|--level2      : player 2 minimax depth"
    print "-g|--genome1     : player 1 genome file"
    print "-G|--genome2     : player 2 genome file"
    print "-h|--help        : show this message and exit"
    return

def main(argv):
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "p:P:l:L:g:G:h",
                                   ["help",
                                    "player1=", "level1=", "genome1=",
                                    "player2=", "level2=", "genome2=", ])
    except getopt.GetoptError as e:
        print str(e)
        usage()
        sys.exit(1)

    player1 = "r"
    player2 = "r"
    level1 = 1
    level2 = 1
    genome1 = "genome.txt"
    genome2 = "genome.txt"
    show_help = False
    for o, a in opts:
        if o in ("-h", "--help"):
            show_help = True
        elif o in ("-p", "--player1"):
            player1 = a
        elif o in ("-P", "--player2"):
            player2 = a
        elif o in ("-l", "--level1"):
            level1 = int(a)
        elif o in ("-L", "--level2"):
            level2 = int(a)
        elif o in ("-l", "--genome1"):
            genome1 = a
        elif o in ("-G", "--genome2"):
            genome2 = a
        else:
            print "Unexpected option: %s" % (o)
            usage()
            sys.exit(1)
    if show_help:
        usage()
        sys.exit(1)
        
    if player1 == "r":
        p1 = TTTRandomPlayer(PLAYER_X)
    elif player1 == "h":
        p1 = TTTHumanPlayer(PLAYER_X)
    elif player1 == "m":
        p1 = TTTMinimaxPlayer(PLAYER_X, level1)
    elif player1 == "g":
        p1 = TTTGenomePlayer.FromGenomeFile(PLAYER_X, genome1)
    else:
        print "Unknown player type: %s." % (player1, )
        usage()
        sys.exit(1)
        
    if player2 == "r":
        p2 = TTTRandomPlayer(PLAYER_O)
    elif player2 == "h":
        p2 = TTTHumanPlayer(PLAYER_O)
    elif player2 == "m":
        p2 = TTTMinimaxPlayer(PLAYER_O, level2)
    elif player2 == "g":
        p2 = TTTGenomePlayer.FromGenomeFile(PLAYER_O, genome2)
    else:
        print "Unknown player type: %s." % (player2, )
        usage()
        sys.exit(1)
        
    g = TTTGame(p1, p2)
    if not g.GameLoop():
        dprint(DEBUG_ERROR, "g.GameLoop() failed.")
        return False
    b = g.GetBoard()
    b.Display()
    
    utility = -1.0
    if player1 == "g":
        utility = p1.Utility(b)
    p1str = "%s:%d:%s:%f" % (p1.__class__.__name__, level1, genome1, utility)
    utility = -1.0
    if player2 == "g":
        utility = p2.Utility(b)
    p2str = "%s:%d:%s:%f" % (p2.__class__.__name__, level2, genome2, utility)

    if b.GetWinner() == PLAYER_X:
        print "Winner is %s." % (p1str, )
    else:
        print "Loser is %s." % (p1str, )

    if b.GetWinner() == PLAYER_O:
        print "Winner is %s." % (p2str, )
    else:
        print "Loser is %s." % (p2str, )
        
    if b.GetWinner() == PLAYER_N or b.GetWinner() == PLAYER_TIE:
        print "Winner is %s." % (b.GetWinner(), )
        
    return

if __name__ == "__main__":
    main(sys.argv)
