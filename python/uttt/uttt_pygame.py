from uttt_data import *
from pygame_game import PygameGame
import pygame
import pygame.locals
import uttt_data
import random
import uttt_ai
import Queue

# colors
very_light_background = (231, 154, 175)
light_background = (193, 96, 122)
normal_background = (154, 51, 79)
dark_background = (116, 19, 45)
very_dark_background = (77, 0, 21)

very_light_player_x = (115, 172, 150)
light_player_x = (72, 144, 117)
normal_player_x = (38, 115, 86)
dark_player_x = (14, 86, 59)
very_dark_player_x = (0, 57, 35)

very_light_player_o = (229, 245, 164)
light_player_o = (185, 204, 102)
normal_player_o = (142, 163, 54)
dark_player_o = (103, 123, 20)
very_dark_player_o = (66, 82, 0)

PIECE_START = 0
PIECE_MOVE = 1
PIECE_DONE = 2


class UTTTGame(PygameGame):

    def __init__(self, width_px, height_px, frames_per_second, data, send_queue, ai_mode, ai_level, ai_send_queue, ai_recv_queue):
        # PygameGame sets self.width and self.height
        PygameGame.__init__(
            self, "Ultimate Tic Tac Toe", width_px, height_px, frames_per_second)
        pygame.font.init()
        self.font = pygame.font.SysFont("Deja Vu Sans Mono", 24)
        self.data = data
        self.send_queue = send_queue
        self.ai_send_queue = ai_send_queue
        self.ai_recv_queue = ai_recv_queue
        self.waiting_for_ai = False
        self.board_top = 100

        self.blink_dir = 1
        self.blink_value = 0
        self.blink_max = frames_per_second

        # for piece movement
        #self.piece_location = [[[5, self.board_top + 5, PIECE_START]
        #                        for pos in range(9)] for bor in range(9)]
        self.piece_location = []
        self.piece_destination = []
        w0 = self.width / 3
        h0 = (self.height - self.board_top) / 3
        for board in range(9):
            dsts = []
            x0 = (board % 3) * w0
            y0 = (board / 3) * h0 + self.board_top
            for position in range(9):
                col = position % 3
                row = position / 3
                x = x0 + int((col + .5) * w0 / 3)
                y = y0 + int((row + .5) * h0 / 3)
                dsts.append((x, y))
            self.piece_destination.append(dsts)
            self.piece_location.append(dsts)

        self.x_images = []
        for i in range(4):
            self.x_images.append(pygame.image.load("XPiece%d.png" % (i,)))
        self.x_image_i = 0
        self.x_image_multiplier = 10

        self.o_images = []
        for i in range(12):
            self.o_images.append(pygame.image.load("OPiece%d.png" % (i,)))
        self.o_image_i = 0
        self.o_image_multiplier = 3

        self.ai_mode = ai_mode
        self.ai_count = self.data.GetMarkerCount() - 1
        self.search_depth = ai_level

        self.game_over = False
        return

    def handle_state(self):
        if self.data:
            state = self.data.GetState()
            if state in [
                uttt_data.STATE_SHOW_SIGNUP, uttt_data.STATE_WAIT_SIGNUP,
                uttt_data.STATE_SIGNUP_FAIL_USERNAME,
                uttt_data.STATE_SHOW_LOGIN, uttt_data.STATE_WAIT_LOGIN, uttt_data.STATE_LOGIN_FAIL,
                uttt_data.STATE_SIGNUP_FAIL_EMAIL, uttt_data.STATE_SIGNUP_FAIL_PASSWORD,
                    uttt_data.STATE_SIGNUP_FAIL_PASSWORD_UNMATCHED, uttt_data.STATE_SIGNUP_OK]:
                # minimize window
                # pygame.display.iconify()
                if self.screen.get_size() != (1, 1):
                    print "shrink"
                    self.screen = pygame.display.set_mode(
                        # set the size
                        (1, 1),
                        # use double-buffering for smooth animation
                        pygame.DOUBLEBUF |
                        # apply alpha blending
                        pygame.SRCALPHA |
                        # allow resizing
                        pygame.RESIZABLE)

            elif state in [
                uttt_data.STATE_WAIT_GAME, uttt_data.STATE_SHOW_GAME,
                    uttt_data.STATE_TURN_FAILED, uttt_data.STATE_WAIT_TURN]:
                # unminimize window
                if self.screen.get_size() != (self.width, self.height):
                    print "WHAT?	pygame doesn't support unminimize?"
                    self.screen = pygame.display.set_mode(
                        # set the size
                        (self.width, self.height),
                        # use double-buffering for smooth animation
                        pygame.DOUBLEBUF |
                        # apply alpha blending
                        pygame.SRCALPHA |
                        # allow resizing
                        pygame.RESIZABLE)
            elif state in [
                uttt_data.STATE_SOCKET_CLOSED, uttt_data.STATE_SOCKET_ERROR,
                    uttt_data.STATE_ERROR, uttt_data.STATE_GAME_OVER]:
                # close
                self.game_over = True
                if self.ai_mode == 'full':
                    print "Socket closed, or other error, pygame will quit."
                    pygame.quit()
            elif state in [uttt_data.STATE_SOCKET_OPEN]:
                # what should I do?
                pass
            else:
                print "Unknown state in pygame: ", state

        return

    def handle_moving_pieces(self):
        for board in range(9):
            for position in range(9):
                if (self.piece_location[board][position][2] == PIECE_START and
                   self.data.GetMarker(board, position) != uttt_data.PLAYER_N):
                    self.piece_location[board][position][2] = PIECE_MOVE
                if self.piece_location[board][position][2] == PIECE_MOVE:
                    x0 = self.piece_location[board][position][0]
                    y0 = self.piece_location[board][position][1]
                    x1 = self.piece_destination[board][position][0]
                    y1 = self.piece_destination[board][position][1]
                    r = random.randrange(3) + 6
                    if x0 < x1:
                        self.piece_location[board][position][0] = x0 + r
                        if self.piece_location[board][position][0] > x1:
                            self.piece_location[board][position][0] = x1
                    r = random.randrange(3) + 6
                    if y0 < y1:
                        self.piece_location[board][position][1] = y0 + r
                        if self.piece_location[board][position][1] > y1:
                            self.piece_location[board][position][1] = y1
                    if x0 >= x1 and y0 >= y1:
                        self.piece_location[board][position][2] = PIECE_DONE
        return

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
        print "pygame: queuing: %s" % (text, )
        self.send_queue.put(text)
        return True

    def screen_position_to_board_and_position(self, mouse_position):
        board, position = -1, -1
        mX, mY = mouse_position[0], mouse_position[1]
        if mY < self.board_top:
            return (board, position)
        col = mX / (self.width / 9)
        row = (mY - self.board_top) / ((self.height - self.board_top) / 9)
        board = 3 * (row / 3) + (col / 3)
        position = 3 * (row % 3) + (col % 3)

        return (board, position)

    def start_ai_think(self):
        if self.ai_mode == 'no':
            return False
        if (not self.waiting_for_ai) and (self.data.GetState() == uttt_data.STATE_SHOW_GAME):
            print "PG->AI: Ask for (depth=%d)" % (self.search_depth, )
            self.ai_send_queue.put(self.search_depth)
            print "PG->AI: put to queue."
            self.waiting_for_ai = True
            return True
        return False

    def play_ai_move(self):
        if self.waiting_for_ai:
            try:
                move = self.ai_recv_queue.get(False)
                print "PG<-AI: recv from queue (%s)." % (move, )
                if move:
                    self.waiting_for_ai = False
                    board, position = move
                    if self.send_turn_if_legal(board, position):
                        self.ai_count = self.data.GetMarkerCount()
                        return True
                    else:
                        print "AI gave bad move:", str(move)
            except Queue.Empty as e:
                # not ready yet, fine
                pass
        return False

    def game_logic(self, keys, newkeys, buttons, newbuttons, mouse_position):
        self.handle_state()
        self.handle_moving_pieces()
        self.x_image_i += 1
        if self.x_image_i >= len(self.x_images) * self.x_image_multiplier:
            self.x_image_i = 0
        self.o_image_i += 1
        if self.o_image_i >= len(self.o_images) * self.o_image_multiplier:
            self.o_image_i = 0

        if self.game_over:
            return True

        if pygame.K_UP in newkeys:
            self.search_depth += 1
        elif pygame.K_DOWN in newkeys:
            self.search_depth -= 1
            if self.search_depth < 1:
                self.search_depth = 1

        if self.play_ai_move():
            return

        if self.ai_mode == 'displaydriven':
            if self.is_my_turn():
                if self.data.GetMarkerCount() > self.ai_count:
                    if self.start_ai_think():
                        return

        if pygame.K_a in newkeys:
            if self.is_my_turn():
                if self.start_ai_think():
                    return

        if 1 in newbuttons:
            if self.is_my_turn():
                (board, position) = self.screen_position_to_board_and_position(
                    mouse_position)
                if self.send_turn_if_legal(board, position):
                    return

        return

    def paint_board(self, surface, board):
        # size and coordinates of the board
        w0 = self.width / 3
        h0 = (self.height - self.board_top) / 3
        x0 = (board % 3) * w0
        y0 = (board / 3) * h0 + self.board_top

        # background/line/piece color
        outline_color = very_light_background
        board_owner = self.data.GetBoardOwner(board)
        if board_owner == uttt_data.PLAYER_N:
            board_is_next = self.is_board_next(board)
            if board_is_next and self.is_my_turn():
                blink_percent = float(self.blink_value) / self.blink_max
                background_color = []
                for i in range(3):
                    background_color.append(
                        int(blink_percent * (very_light_background[i] - normal_background[i])) + normal_background[i])

                # light background where I can play, if it's my turn
                line_color = very_dark_background
                player_x_color = normal_player_x
                player_o_color = normal_player_o
            elif board_is_next and self.is_your_turn():
                blink_percent = float(self.blink_value) / self.blink_max
                background_color = []
                for i in range(3):
                    background_color.append(
                        int(blink_percent * (normal_background[i] - very_dark_background[i])) + very_dark_background[i])

                # dark background where you can play, if it's your turn
                line_color = very_light_background
                player_x_color = normal_player_x
                player_o_color = normal_player_o
            else:
                # normal background where I can't play
                background_color = normal_background
                line_color = very_dark_background
                player_x_color = normal_player_x
                player_o_color = normal_player_o
        elif board_owner == uttt_data.PLAYER_X:
            background_color = light_player_x
            line_color = very_dark_player_x
            player_x_color = dark_player_x
            player_o_color = very_light_player_o
        elif board_owner == uttt_data.PLAYER_O:
            background_color = light_player_o
            line_color = very_dark_player_o
            player_x_color = very_light_player_x
            player_o_color = dark_player_o
        else:
            # error
            background_color = (0, 0, 0)
            line_color = (255, 255, 255)
            player_x_color = normal_player_x
            player_o_color = normal_player_o

        # outline
        rect = pygame.Rect(x0, y0, w0, h0)
        surface.fill(outline_color, rect)

        # background
        rect = pygame.Rect(x0 + 2, y0 + 2, w0 - 4, h0 - 4)
        surface.fill(background_color, rect)

        # lines
        for i in range(1, 3):
            x = x0 + (i * w0 / 3)
            y1 = y0
            y2 = y0 + h0
            pygame.draw.line(surface, line_color, (x, y1), (x, y2))

            x1 = x0
            x2 = x0 + w0
            y = y0 + (i * h0 / 3)
            pygame.draw.line(surface, line_color, (x1, y), (x2, y))

        # markers
        for position in range(9):
            x = self.piece_location[board][position][0]
            y = self.piece_location[board][position][1]
            marker = self.data.GetMarker(board, position)
            if marker == uttt_data.PLAYER_X:
                if self.piece_location[board][position][2] == PIECE_MOVE:
                    i = self.x_image_i / self.x_image_multiplier
                else:
                    i = 0
                (ww, hh) = self.x_images[i].get_size()
                surface.blit(self.x_images[i], (x - ww / 2, y - hh / 2))
                # pygame.draw.circle(surface, player_x_color, (x, y), 5)
            elif marker == uttt_data.PLAYER_O:
                if self.piece_location[board][position][2] == PIECE_MOVE:
                    i = self.o_image_i / self.o_image_multiplier
                else:
                    i = 0
                (ww, hh) = self.o_images[i].get_size()
                surface.blit(self.o_images[i], (x - ww / 2, y - hh / 2))
                # pygame.draw.circle(surface, player_o_color, (x, y), 5)

        return

    def paint_game_info(self, surface):
        my_turn = self.is_my_turn()
        your_turn = self.is_your_turn()
        player = self.data.GetPlayer()
        player_extra = ""
        opponent_extra = ""
        if player == uttt_data.PLAYER_X:
            opponent = uttt_data.PLAYER_O
            if my_turn:
                player_color = very_light_player_x
                opponent_color = normal_player_o
                player_extra = " * "
            elif your_turn:
                player_color = normal_player_x
                opponent_color = very_light_player_o
                opponent_extra = " * "
            else:
                player_color = normal_player_x
                opponent_color = normal_player_o
        else:
            opponent = uttt_data.PLAYER_X
            if my_turn:
                player_color = very_light_player_o
                opponent_color = normal_player_x
                player_extra = " * "
            elif your_turn:
                player_color = normal_player_o
                opponent_color = very_light_player_x
                opponent_extra = " * "
            else:
                player_color = normal_player_o
                opponent_color = normal_player_x

        self.drawTextLeft(surface, player + " " + self.data.GetPlayerName()
                          + player_extra, 30, 45, self.font, player_color)
        self.drawTextLeft(surface, opponent + " " + self.data.GetOpponentName()
                          + opponent_extra, 30, 75, self.font, opponent_color)
        if self.game_over:
            winner = self.data.GetWinner()
            if winner == player:
                winner_str = self.data.GetPlayerName() + " wins!"
            elif winner == opponent:
                winner_str = self.data.GetOpponentName() + " wins!"
            elif winner == uttt_data.PLAYER_TIE:
                winner_str = "Cat wins."
            else:
                winner_str = "Shouldn't get this message."
            self.drawTextRight(
                surface, winner_str, self.width - 30, 45, self.font, player_color)
        else:
            self.drawTextRight(surface, "Search depth: " + str(
                self.search_depth), self.width - 30, 45, self.font, player_color)
            if self.waiting_for_ai:
                self.drawTextRight(
                    surface, "Thinking...", self.width - 30, 75, self.font, player_color)
        return

    def paint(self, surface):
        # Blink control
        self.blink_value += self.blink_dir
        if self.blink_value >= self.blink_max:
            self.blink_value = self.blink_max
            self.blink_dir = -1
        elif self.blink_value <= 0:
            self.blink_value = 0
            self.blink_dir = 1

        # Background
        rect = pygame.Rect(0, 0, self.width, self.height)
        surface.fill(light_background, rect)

        for board in range(9):
            self.paint_board(surface, board)

        self.paint_game_info(surface)

        return

    # Draws a transparent rectangle
    # note that color should have an alpha channel (4th element)
    def drawTransparentRect(self, surface, color, rect):
        rect_surface = pygame.Surface(
            (rect.width, rect.height), pygame.locals.SRCALPHA)
        rect_surface.fill((0, 0, 0, 0))
        r = pygame.Rect(0, 0, rect.width, rect.height)
        pygame.draw.rect(rect_surface, color, r)
        surface.blit(rect_surface, (rect.left, rect.top))
        return

    # Draws text left justified at "x".
    # The bottom of the text is displayed at "y".
    def drawTextLeft(self, surface, text, x, y, font, color):
        text_object = font.render(text, False, color)
        text_rect = text_object.get_rect()
        text_rect.bottomleft = (x, y)
        surface.blit(text_object, text_rect)
        return text_rect

    # Draws text right justified at "x".
    # The bottom of the text is displayed at "y".
    def drawTextRight(self, surface, text, x, y, font, color):
        text_object = font.render(text, False, color)
        text_rect = text_object.get_rect()
        text_rect.bottomright = (x, y)
        surface.blit(text_object, text_rect)
        return

    # Draws text centered at "x".
    # The middle of the text is displayed at "y".
    def drawTextCenter(self, surface, text, x, y, font, color):
        text_object = font.render(text, False, color)
        text_rect = text_object.get_rect()
        text_rect.center = (x, y)
        surface.blit(text_object, text_rect)
        return


def uttt_pygame_main(data, send_queue, ai_mode, ai_level, ai_send_queue, ai_recv_queue):
    game = UTTTGame(600, 700, 30, data, send_queue,
                    ai_mode, ai_level, ai_send_queue, ai_recv_queue)
    game.main_loop()
    return

if __name__ == "__main__":
    data = UTTTData()
    data.SetState(uttt_data.STATE_SHOW_GAME)
    data.SetBoardMarker(6, 8, uttt_data.PLAYER_X)
    data.SetBoardMarker(8, 2, uttt_data.PLAYER_O)
    data.SetNextTurn(4, uttt_data.PLAYER_X)
    data.SetThisPlayer(uttt_data.PLAYER_X, "ME")
    data.SetOtherPlayer("YOU")
    uttt_pygame_main(data, None, False, 5, None, None)
