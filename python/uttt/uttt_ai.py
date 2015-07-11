import sys
sys.path.append('..')
import neat
import uttt_data
import Queue
import time, random, os


class Board:

    def __init__(self, data):
        self.markers = [[data.GetMarker(board, position)
                         for position in range(9)] for board in range(9)]
        self.next_player = data.GetNextPlayer()
        self.next_board = data.GetNextBoard()
        self.winner = data.GetWinner()
        self.board_owners = [data.GetBoardOwner(board) for board in range(9)]
        self.this_player = data.GetPlayer()
        if self.this_player == uttt_data.PLAYER_X:
            self.other_player = uttt_data.PLAYER_O
        else:
            self.other_player = uttt_data.PLAYER_X
        return

    def GetMarker(self, b, p):
        return self.markers[b][b]
        
    def GetThisPlayer(self):
        return self.this_player

    def GetNextBoard(self):
        return self.next_board
        

    def CheckBoardWin(self, b):
        wins = [[0, 1, 2],
               [3, 4, 5],
               [6, 7, 8],
               [0, 3, 6],
               [1, 4, 7],
               [2, 5, 8],
               [0, 4, 8],
               [2, 4, 6],
                ]
        for w in wins:
            if b[w[0]] == b[w[1]] and b[w[0]] == b[w[2]] and b[w[0]] != uttt_data.PLAYER_N:
                return b[w[0]]
        return uttt_data.PLAYER_N

    def MakeMove(self, move):
        board, position = move
        undo_info = (board, position, self.markers[board][position],
                     self.next_player, self.next_board, self.board_owners[board], self.winner)

        self.markers[board][position] = self.next_player
        if self.next_player == uttt_data.PLAYER_X:
            self.next_player = uttt_data.PLAYER_O
        else:
            self.next_player = uttt_data.PLAYER_X
        self.next_board = position
        self.board_owners[board] = self.CheckBoardWin(self.markers[board])
        if self.board_owners[self.next_board] != uttt_data.PLAYER_N:
            self.next_board = uttt_data.BOARD_ANY
        self.winner = self.CheckBoardWin(self.board_owners)

        return undo_info

    def UndoMove(self, undo_info):
        (b, p, m, np, nb, bo, w) = undo_info
        self.markers[b][p] = m
        self.next_player = np
        self.next_board = nb
        self.board_owners[b] = bo
        self.winner = w
        return

    def PositionScore(self, position, scores):
        if position in [0, 2, 6, 8]:
            score = scores[0]
        elif position in [1, 3, 5, 7]:
            score = scores[2]
        elif position in [4]:
            score = scores[1]
        else:
            score = 0
        return score

    def Evaluate(self):
        POSITION_EDGE_SCORE = 1
        POSITION_CORNER_SCORE = POSITION_EDGE_SCORE * 3
        POSITION_CENTER_SCORE = POSITION_CORNER_SCORE * 3
        BOARD_EDGE_SCORE = POSITION_EDGE_SCORE * 1000
        BOARD_CORNER_SCORE = POSITION_CORNER_SCORE * 1000
        BOARD_CENTER_SCORE = POSITION_CENTER_SCORE * 1000
        GAME_WIN_SCORE = BOARD_CENTER_SCORE * 1000
        BOARD_SCORES = [
            BOARD_CORNER_SCORE, BOARD_CENTER_SCORE, BOARD_EDGE_SCORE]
        POSITION_SCORES = [
            POSITION_CORNER_SCORE, POSITION_CENTER_SCORE, POSITION_EDGE_SCORE]
        score = 0
        if self.winner != uttt_data.PLAYER_N:
            if self.winner == self.this_player:
                score += GAME_WIN_SCORE
            elif self.winner == self.other_player:
                score -= GAME_WIN_SCORE
        else:
            for board in range(9):
                if self.board_owners[board] == self.this_player:
                    score += self.PositionScore(board, BOARD_SCORES)
                elif self.board_owners[board] == self.other_player:
                    score -= self.PositionScore(board, BOARD_SCORES)
                else:
                    for position in range(9):
                        if self.markers[board][position] == self.this_player:
                            score += self.PositionScore(
                                position, POSITION_SCORES)
                        elif self.markers[board][position] == self.other_player:
                            score -= self.PositionScore(
                                position, POSITION_SCORES)
        return score

    def EvaluateGenome(self):
        POSITION_WIN_SCORE  =  0.010
        POSITION_LOSE_SCORE = -0.005
        BOARD_WIN_SCORE     =  0.100
        BOARD_LOSE_SCORE    = -0.050
        GAME_WIN_SCORE      =  1.000
        GAME_LOSE_SCORE     = -1.000
        score = 0.
        if self.winner != uttt_data.PLAYER_N:
            if self.winner == self.this_player:
                score += GAME_WIN_SCORE
            elif self.winner == self.other_player:
                score += GAME_LOSE_SCORE
        else:
            for board in range(9):
                if self.board_owners[board] == self.this_player:
                    score += BOARD_WIN_SCORE
                elif self.board_owners[board] == self.other_player:
                    score += BOARD_LOSE_SCORE
                else:
                    for position in range(9):
                        if self.markers[board][position] == self.this_player:
                            score += POSITION_WIN_SCORE
                        elif self.markers[board][position] == self.other_player:
                            score += POSITION_LOSE_SCORE
        return score
        
    def EvaluateTurnsOnly(self):
        POSITION_WIN_SCORE  =  0.010
        POSITION_LOSE_SCORE = -0.005
        BOARD_WIN_SCORE     =  0.100
        BOARD_LOSE_SCORE    = -0.050
        GAME_WIN_SCORE      =  1.000
        GAME_LOSE_SCORE     = -1.000
        score = 0.
        for board in range(9):
            for position in range(9):
                if self.markers[board][position] == self.this_player:
                    score += POSITION_WIN_SCORE
        return score

    def LegalMoves(self):
        moves = []
        if self.next_board == uttt_data.BOARD_ANY:
            board_list = range(9)
        else:
            board_list = [self.next_board]
        for board in board_list:
            if self.board_owners[board] != uttt_data.PLAYER_N:
                continue
            for position in range(9):
                if self.markers[board][position] != uttt_data.PLAYER_N:
                    continue
                moves.append((board, position))
        return moves


class UTTTAI:

    def __init__(self, data, send_queue, ai_send_queue, ai_recv_queue, no_gui, ai_level, results_file, genome_file,
                 ai_type, ai_mode):
        self.data = data
        self.send_queue = send_queue
        self.ai_send_queue = ai_send_queue
        self.ai_recv_queue = ai_recv_queue
        self.INFINITY = 1000000000
        self.no_gui = no_gui
        self.ai_level = ai_level
        self.results_file = results_file
        self.genome_file = genome_file
        self.ai_type = ai_type
        self.ai_mode = ai_mode
        if (self.ai_type == 'genome' or self.ai_type == 'genomelearn'):
            if self.ai_type == 'genomelearn':
                if os.path.exists(self.results_file):
                    os.remove(self.results_file)
            print "ai_type:", self.ai_type
            self.LoadGenome()
        elif self.ai_type == 'minimax':
            print "ai_type:", self.ai_type
            pass
        else:
            print "Unknown ai type: (%s)" % (self.ai_type, )
            sys.exit(1)
        return

        
    def ChooseMove(self, depth):
        if self.ai_type == 'minimax':
            return self.ChooseMoveMiniMax(depth)
        elif self.ai_type == 'genome' or self.ai_type == 'genomelearn':
            return self.ChooseMoveGenome()
        else:
            print "Unknown ai type:", self.ai_type
            return (0, 0)

    ######
    ######  Genome code
    ######
    def LoadGenome(self):
        new_genome = neat.Genome.new_Genome_load(self.genome_file)
        new_organism = neat.Organism()
        new_organism.SetFromGenome(0., new_genome, 1, "UTTT AI")

        self.organism = new_organism
        return

    def ChooseMoveGenome(self):
        #
        # UTTT information
        #
        move = (0, 0)
        board = Board(self.data)
        me = board.GetThisPlayer()

        #
        # ANN information
        #
        net = self.organism.net
        numnodes = len(self.organism.gnome.nodes)
        net_depth = net.max_depth()

        #
        # set the inputs for the network from the board data
        inv = [ 1. ] # BIAS

        # markers
        # first 81 = other player's
        # second 81 = mine
        #
        for b in range(9):
            for p in range(9):
                m = board.GetMarker(b, p)
                if m == uttt_data.PLAYER_N:
                    v = 0.0
                elif m == me:
                    v = 0.0
                else:
                    v = 1.0
                inv.append(v)

        for b in range(9):
            for p in range(9):
                m = board.GetMarker(b, p)
                if m == uttt_data.PLAYER_N:
                    v = 0.0
                elif m == me:
                    v = 1.0
                else:
                    v = 0.0
                inv.append(v)

        # need to load next board here
        nb = board.GetNextBoard()
        for b in range(9):
            if nb == -1 or b == nb:
                v = 1.0
            else:
                v = 0.0
            inv.append(v)
        net.load_sensors(inv)

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

        # choose the board
        max_i = 0
        max_v = net.outputs[0].activation
        for i in range(1,9):
            if ((max_v < net.outputs[i].activation) or
                ((max_v == net.outputs[i].activation) and (random.random() > 0.5))):
                max_i = i
                max_v = net.outputs[i].activation
        b = max_i
        
        # choose the position
        max_i = 9
        max_v = net.outputs[9].activation
        for i in range(10,18):
            if ((max_v < net.outputs[i].activation) or
                ((max_v == net.outputs[i].activation) and (random.random() > 0.5))):
                max_i = i
                max_v = net.outputs[i].activation
        p = max_i - 9
        move = (b, p)

        # clear the network to be ready for next turn
        net.flush()
                
        return move
    ######
            
    def ChooseMoveMiniMax(self, depth):
        if self.data.GetState() != uttt_data.STATE_SHOW_GAME:
            return None
        board = Board(self.data)
        alpha = - 2 * self.INFINITY
        beta = 2 * self.INFINITY
        self.evaluations = 0
        (move, value) = self.Max(board, depth, alpha + 0, beta + 0)
        print "Chose %s for %d in %d evaluations." % (str(move), int(value), int(self.evaluations))
        return move

    def Max(self, board, depth, alpha, beta):
        if depth <= 0 or board.winner != uttt_data.PLAYER_N:
            self.evaluations += 1
            return (None, board.Evaluate())
        max_value = - self.INFINITY
        max_move = None
        moves = board.LegalMoves()
        for m in moves:
            undo_info = board.MakeMove(m)
            (junk, value) = self.Min(board, depth - 1, alpha + 0, beta + 0)
            board.UndoMove(undo_info)
            if value > max_value:
                max_value = value
                max_move = m
            if value > alpha:
                alpha = value
            if alpha >= beta:
                break
        return (max_move, max_value)

    def Min(self, board, depth, alpha, beta):
        if depth <= 0 or board.winner != uttt_data.PLAYER_N:
            self.evaluations += 1
            return (None, board.Evaluate())
        min_value = self.INFINITY
        min_move = None
        moves = board.LegalMoves()
        for m in moves:
            undo_info = board.MakeMove(m)
            (junk, value) = self.Max(board, depth - 1, alpha + 0, beta + 0)
            board.UndoMove(undo_info)
            if value < min_value:
                min_value = value
                min_move = m
            if value < beta:
                beta = value
            if alpha >= beta:
                break
        return (min_move, min_value)

    def is_my_turn(self):
        next_player = self.data.GetNextPlayer()
        player = self.data.GetPlayer()
        return next_player == player and next_player != uttt_data.PLAYER_N

    def is_your_turn(self):
        next_player = self.data.GetNextPlayer()
        player = self.data.GetPlayer()
        return next_player != player and next_player != uttt_data.PLAYER_N

    def is_board_next(self, board):
        next_board = self.data.GetNextBoard()
        return next_board == board or next_board == uttt_data.BOARD_ANY

    def send_turn_if_legal(self, board, position):
        # Legal values for board, position?
        if board < 0 or board > 8 or position < 0 or position > 8:
            print "Bad board=%d or position=%d" % (int(board), int(position))
            return False
        # Game on, and not waiting for an update?
        if self.data.GetState() != uttt_data.STATE_SHOW_GAME:
            print "Bad state=%d" % (int(self.data.GetState()), )
            return False
        # Our turn?
        if not self.is_my_turn():
            print "Bad turn next_player=%s != player=%s" % (str(self.data.GetNextPlayer()),
                                                            str(self.data.GetPlayer()))
            return False
        # Legal board?
        if not self.is_board_next(board):
            print "Bad next_board next_board=%d != board=%d" % (int(self.data.GetNextBoard()), int(board))
            return False
        # Board not won?
        if self.data.GetBoardOwner(board) != uttt_data.PLAYER_N:
            print "Bad board_owner(board=%d)=%s" % (int(board), str(self.data.GetBoardOwner(board)))
            return False
        # Position empty?
        if self.data.GetMarker(board, position) != uttt_data.PLAYER_N:
            print "Bad marker(board=%d, position=%d)=%s" % (int(board), int(position),
                                                            str(self.data.GetMarker(board, position)))
            return False
        # Data connection and queue open?
        if (not self.data) or (not self.send_queue):
            print "Bad data=%s or send_queue=%s" % (str(self.data), str(self.send_queue))
            return False
        # OK, send it
        text = self.data.SendTurn(board, position)
        print "ai: queuing: %s" % (text, )
        self.send_queue.put(text)
        return True

    def main_loop(self):
        count = 0
        while not ( self.data.GetState( ) in [uttt_data.STATE_SOCKET_CLOSED, uttt_data.STATE_SOCKET_ERROR,
                                              uttt_data.STATE_ERROR, uttt_data.STATE_GAME_OVER] ):
            try:
                if self.no_gui or self.ai_mode == 'full':
                    if not (self.is_my_turn() and self.data.GetState() == uttt_data.STATE_SHOW_GAME):
                        # print "AI: Waiting for my turn."
                        time.sleep(.5)
                        continue
                    depth = self.ai_level
                else:
                    depth = self.ai_send_queue.get(True, 1)

                print "AI: ChooseMove(%d)" % (depth, )
                move = self.ChooseMove(depth)
                count += 1

                if self.no_gui or self.ai_mode == 'full':
                    board, position = move
                    if self.send_turn_if_legal(board, position):
                        #self.data.Display()
                        print "AI: SendMove(%d,%d)" % (board, position)
                        
                    if self.ai_type == "genomelearn" and count > 45:
                        print "AI: Maximum count completed"
                        self.send_queue.put("QUIT")
                        break

                else:
                    self.ai_recv_queue.put(move)
                    print "AI: put to queue"

            except Queue.Empty as e:
                # not ready yet, fine
                pass

        board = Board(self.data)
        print "Final Score:", board.Evaluate()
        if self.ai_type == 'genomelearn':
            fout = open(self.results_file, "w")
            s = str(board.EvaluateTurnsOnly()) + "\n"
            fout.write(s)
            fout.close()
            print "TurnsScore:", board.EvaluateTurnsOnly()
        return


def uttt_ai_main(data, send_queue, ai_send_queue, ai_recv_queue, no_gui, ai_level, results_file, genome_file, ai_type,
                 ai_mode):
    ai = UTTTAI(data, send_queue, ai_send_queue,
                ai_recv_queue, no_gui, ai_level,
                results_file, genome_file, ai_type, ai_mode)
    ai.main_loop()
    return
