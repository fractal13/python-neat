import sys
sys.path.append("..")
from neat.utils import matching_import
from neat.debug import dprint
from neat import debug as debug
matching_import("DEBUG_.*", debug, globals())

from ttt_player import TTTPlayer
from ttt_board import *

import random


INFINITY = 1000000000
DEPTH_SCALE = 0.999

class TTTMinimaxBoard(TTTBoard):

    def __init__(self, board):
        self.board = [ m for m in board.board ]
        self.next_player = board.next_player
        self.winner = board.winner
        return

    def MakeMove(self, position, player):
        undo_info = (position, self.board[position], self.next_player, self.winner)
        self.TakeTurn(position, player)
        return undo_info

    def UndoMove(self, undo_info):
        (position, marker, next_player, winner) = undo_info
        self.board[position] = marker
        self.next_player = next_player
        self.winner = winner
        return


class TTTMinimaxPlayer(TTTPlayer):

    def __init__(self, player, max_depth):
        TTTPlayer.__init__(self, player)
        self.max_depth = max_depth
        self.other = None
        return

    def ChooseMove(self, board):

        alpha = -2 * INFINITY
        beta = 2 * INFINITY
        
        self.other = board.OtherPlayer(self.player)

        #print "Before:"
        #board.Display()
        move, value = self.Max(TTTMinimaxBoard(board), self.max_depth, alpha + 0, beta + 0)
        print "After: (Choice: %d)" % (move, )
        board.Display()
        #print
        
        return move

    def Max(self, board, depth, alpha, beta):
        if depth <= 0 or board.GetWinner() != PLAYER_N:
            return (None, self.Evaluate(board))

        children = []
        max_value = - INFINITY
        max_moves = [ None ]
        moves = board.GetLegalMoves()
        for m in moves:
            undo_info = board.MakeMove(m, self.player)
            (junk, value) = self.Min(board, depth - 1, alpha + 0, beta + 0)
            children.append( (m, value) )
            board.UndoMove(undo_info)
            if value > max_value:
                max_value = value
                max_moves = [ m ]
            elif value == max_value:
                max_moves.append( m )
            if value > alpha:
                alpha = value
            if alpha > beta:
                break
        print "MAX", depth, len(children), len(moves), alpha, beta, max_value, children
        return (random.choice(max_moves), DEPTH_SCALE * max_value)

    def Min(self, board, depth, alpha, beta):
        if depth <= 0 or board.GetWinner() != PLAYER_N:
            return (None, self.Evaluate(board))

        children = []
        min_value = INFINITY
        min_moves = [ None ]
        moves = board.GetLegalMoves()
        for m in moves:
            undo_info = board.MakeMove(m, self.other)
            (junk, value) = self.Max(board, depth - 1, alpha + 0, beta + 0)
            children.append( (m, value) )
            board.UndoMove(undo_info)
            if value < min_value:
                min_value = value
                min_moves = [ m ]
            elif value == min_value:
                min_moves.append( m )
            if value < beta:
                beta = value
            if alpha > beta:
                break
        print "MIN", depth, len(children), len(moves), alpha, beta, min_value, children
        return (random.choice(min_moves), DEPTH_SCALE * min_value)

    def PositionValue(self, position):
        if position in [ 4 ]:
            return 0.0003
        elif position in [ 0, 2, 6, 8 ]:
            return 0.0002
        elif position in [ 1, 3, 5, 7 ]:
            return 0.0001
        
    def Evaluate(self, board):
        winner = board.GetWinner()
        
        v = 0
        if winner == self.player:
            v = 1.0
        elif winner == self.other:
            v = -1.0
        elif winner == PLAYER_TIE:
            v = 0.0
        else:
            for position in range(9):
                marker = board.GetMarker(position)
                if marker == PLAYER_N:
                    np = board.next_player
                    
                    board.next_player = self.player
                    undo_info = board.MakeMove(position, self.player)
                    if board.GetWinner() == self.player:
                        v += 0.01
                    board.UndoMove(undo_info)
                    
                    board.next_player = self.other
                    undo_info = board.MakeMove(position, self.other)
                    if board.GetWinner() == self.other:
                        v -= 0.01
                    board.UndoMove(undo_info)

                    board.next_player = np

                elif marker == self.player:
                    v += self.PositionValue(position)
                        
                elif marker == self.other:
                    v -= self.PositionValue(position)
                    
        return v


        
