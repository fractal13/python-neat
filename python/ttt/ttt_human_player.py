from ttt_player import TTTPlayer
import random

class TTTHumanPlayer(TTTPlayer):

    def __init__(self, player):
        TTTPlayer.__init__(self, player)
        return

    def ChooseMove(self, board):
        legal = board.GetLegalMoves()
        m = -1
        while m not in legal:
            print
            print "You are %s." % (self.player, )
            board.Display()
            ans = raw_input("Choice [%s]? " % ( ":".join([ str(m) for m in legal]) ,))
            if len(ans) > 0 and ans[0] >= '0' and ans[0] <= '9':
                m = int(ans[0])
        return m
        
        


        
