import sys
sys.path.append("..")
from neat.utils import matching_import
from neat.debug import dprint
from neat import debug as debug
matching_import("DEBUG_.*", debug, globals())
import neat

from ttt_player import TTTPlayer
from ttt_board import *

import random

class TTTGenomePlayer(TTTPlayer):

    def __init__(self, player, organism):
        TTTPlayer.__init__(self, player)
        self.organism = organism
        self.other = None
        return

    @classmethod
    def FromGenomeFile(cls, player, genome_file):
        
        new_genome = neat.Genome.new_Genome_load(genome_file)
        new_organism = neat.Organism()
        new_organism.SetFromGenome(0., new_genome, 1, "TTT AI")

        obj = cls(player, new_organism)
        
        return obj

    def ChooseMove(self, board):
        
        self.other = board.OtherPlayer(self.player)

        #
        # ANN information
        #
        net = self.organism.net
        numnodes = len(self.organism.gnome.nodes)
        net_depth = net.max_depth()

        # network input structure:
        # BIAS, OPPONENT * 9, ME * 9
        # network output structure:
        # POSITION * 9

        #
        # set the inputs for the network from the board data
        #
        
        # BIAS
        input_values = [ 1. ]
        
        # Opponent
        for position in range(9):
            marker = board.GetMarker(position)
            if marker == self.other:
                v = 1.0
            else:
                v = -1.0
            input_values.append(v)

        # Me
        for position in range(9):
            marker = board.GetMarker(position)
            if marker == self.player:
                v = 1.0
            else:
                v = -1.0
            input_values.append(v)

        net.load_sensors(input_values)

        #
        # process inputs through the network
        #
        
        #//Relax net and get output
        success = net.activate()
        #//use depth to ensure relaxation
        for relax in range(0, net_depth+1):
            success = net.activate()

            
        #
        # Read and interpret the outputs
        #

        # choose the position
        max_i = [ 0 ]
        max_v = net.outputs[0].activation
        for i in range(1,9):
            if max_v < net.outputs[i].activation:
                max_i = [ i ]
                max_v = net.outputs[i].activation
            elif max_v == net.outputs[i].activation:
                max_i.append( i )

        move = random.choice(max_i)
        
        # clear the network to be ready for next turn
        net.flush()
        
        return move


    def PositionValue(self, position):
        if position in [ 4 ]:
            return 0.00013
        elif position in [ 0, 2, 6, 8 ]:
            return 0.00012
        elif position in [ 1, 3, 5, 7 ]:
            return 0.00011
        
    def Utility(self, board):
        """
        ranges from 0 to 1
        
        """
        winner = board.GetWinner()
        
        v = 0
        if winner == self.player:
            v = 1.0
        elif winner == self.other:
            v = 0.0
        elif winner == PLAYER_TIE:
            v = 0.5
        else:
            for position in range(9):
                marker = board.GetMarker(position)
                if marker == self.player:
                    v += self.PositionValue(position)
                    
        return v


        
