from ttt_player import TTTPlayer
import random

class TTTRandomPlayer(TTTPlayer):

    def __init__(self, player):
        TTTPlayer.__init__(self, player)
        return

    def ChooseMove(self, board):
        return random.choice( board.GetLegalMoves() )
        


        
