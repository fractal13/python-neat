import uttt_messages
import re, sys

PLAYER_N = "N"
PLAYER_X = "X"
PLAYER_O = "O"
PLAYER_TIE = "TIE"
LEGAL_BOARD_OWNERS = (PLAYER_X, PLAYER_O, PLAYER_TIE)
LEGAL_MARKERS = (PLAYER_X, PLAYER_O)
BOARD_ANY = -1

STATE_SHOW_SIGNUP = 1
STATE_WAIT_SIGNUP = 2
STATE_SIGNUP_FAIL_USERNAME = 3
STATE_SHOW_LOGIN = 4
STATE_WAIT_LOGIN = 5
STATE_LOGIN_FAIL = 6
STATE_WAIT_GAME = 7
STATE_SHOW_GAME = 8
STATE_GAME_OVER = 9
STATE_TURN_FAILED = 10
STATE_SIGNUP_FAIL_EMAIL = 11
STATE_SIGNUP_FAIL_PASSWORD = 12
STATE_SIGNUP_FAIL_PASSWORD_UNMATCHED = 13
STATE_ERROR = 14
STATE_WAIT_TURN = 15
STATE_SOCKET_CLOSED = 16
STATE_SOCKET_ERROR = 17
STATE_SOCKET_OPEN = 18
STATE_SIGNUP_OK = 19

g_debug = False


class UTTTData:

    def __init__(self):
        self.board = [[PLAYER_N for i in range(9)] for j in range(9)]
        self.next_player = PLAYER_N
        self.next_board = BOARD_ANY
        self.winner = PLAYER_N
        self.board_owners = [	 PLAYER_N for i in range(9)]

        self.this_player = PLAYER_N
        self.this_name = ""
        self.other_name = ""

        self.login_name = ""
        self.login_password = ""
        self.logged_in = False

        self.state = STATE_SHOW_LOGIN

        return

    def Display(self):
        for row in range(9):
            if row % 3 == 0:
                print "+-------+-------+-------+"
            line = ""
            for col in range(9):
                if col % 3 == 0:
                    line += "| "
                b = 3 * (row / 3) + (col / 3)
                p = 3 * (row % 3) + (col % 3)
                line += str(self.board[b][p]) + " "
            print line + "|"
        print "+-------+-------+-------+"
        print
        print "Next:", self.next_player, "	", self.next_board
        print "Winner", self.winner
        print "Owners:", " ".join(self.board_owners)
        print "Me:", self.this_player, self.this_name
        print "You:", self.other_name
        print "State:", self.state,	 self.logged_in
        print
        return True

    def SetState(self, state):
        self.state = state
        return True

    def GetMarkerCount(self):
        count = 0
        for board in range(9):
            for position in range(9):
                if self.board[board][position] in [PLAYER_X, PLAYER_O]:
                    count += 1
        return count

    def GetMarker(self, board, position):
        if self.LegalBoardIndex(board) and self.LegalPositionIndex(board, position):
            return self.board[board][position]
        return PLAYER_N

    def GetNextPlayer(self):
        return self.next_player

    def GetNextBoard(self):
        return self.next_board

    def GetWinner(self):
        return self.winner

    def GetBoardOwner(self, board):
        if self.LegalBoardIndex(board):
            return self.board_owners[board]
        return PLAYER_N

    def GetPlayer(self):
        return self.this_player

    def GetPlayerName(self):
        return self.this_name

    def GetOpponentName(self):
        return self.other_name

    def GetLoginName(self):
        return self.login_name

    def GetLoginPassword(self):
        return self.login_password

    def GetLoggedIn(self):
        return self.logged_in

    def GetState(self):
        return self.state

    def LegalBoardIndex(self, board):
        return board >= 0 and board < len(self.board)

    def LegalPositionIndex(self, board, position):
        return self.LegalBoardIndex and position >= 0 and position < len(self.board[board])

    def SetBoardOwner(self, board, player):
        if self.LegalBoardIndex(board) and player in LEGAL_BOARD_OWNERS:
            self.board_owners[board] = player
            return True
        return False

    def SetBoardMarker(self, board, position, player):
        if self.LegalPositionIndex(board, position) and player in LEGAL_MARKERS:
            self.board[board][position] = player
            return True
        return False

    def SetNextTurn(self, board, player):
        if (board == BOARD_ANY or self.LegalBoardIndex(board)) and player in LEGAL_MARKERS:
            self.next_player = player
            self.next_board = board
            self.state = STATE_WAIT_GAME  # waiting for update finished message
            return True
        return False

    def SendTurn(self, board, position):
        # check board is legal
        # check board isn't won
        # check position is legal
        # check board position is empty
        # check is my turn
        if (((self.next_board == BOARD_ANY and self.LegalBoardIndex(board)) or self.next_board == board)
           and self.board_owners[board] == PLAYER_N
           and self.LegalPositionIndex(board, position) and self.board[board][position] == PLAYER_N
           and self.next_player == self.this_player and self.next_player != PLAYER_N):

            self.state = STATE_WAIT_TURN
            msg = uttt_messages.TurnMsg(self.this_player, board, position)
            return uttt_messages.Serialize(msg)
        return ""

    def SendUpdate(self):
        msg = uttt_messages.UpdateMsg()
        return uttt_messages.Serialize(msg)

    def SendWhoami(self):
        msg = uttt_messages.WhoamiMsg()
        return uttt_messages.Serialize(msg)
        return True

    def SetWinner(self, player):
        if player in LEGAL_BOARD_OWNERS:
            self.winner = player
            self.state = STATE_GAME_OVER
            #self.Display()
            return True
        return False

    def SetThisPlayer(self, player, player_name):
        if player in LEGAL_MARKERS:
            self.this_player = player
            self.this_name = player_name
            return True
        return False

    def SetTurnFailed(self):
        self.state = STATE_TURN_FAILED
        return True

    def ShowLogin(self):
        if self.state == STATE_WAIT_LOGIN or self.state == STATE_SHOW_SIGNUP or self.state == STATE_LOGIN_FAIL:
            self.state = STATE_SHOW_LOGIN
            return True
        return False

    def SendLogin(self, email, password):
        if self.state == STATE_SHOW_LOGIN or self.state == STATE_SIGNUP_OK:
            email = re.sub(" ", "", email)
            password = re.sub(" ", "", password)
            if email != "" and password != "":
                self.login_name = email
                self.login_password = password
                self.state = STATE_WAIT_LOGIN
                msg = uttt_messages.LoginMsg(email, password)
                return uttt_messages.Serialize(msg)
        return ""

    def SetLoginStatus(self, valid):
        print "CurrentState:", self.state
        if self.state == STATE_WAIT_LOGIN:
            if valid:
                self.state = STATE_WAIT_GAME
                self.logged_in = True
            else:
                self.state = STATE_LOGIN_FAIL
                self.login_name = ""
                self.login_password = ""
                self.logged_in = False
            print "CurrentState:", self.state
            return True
        return False

    def ShowSignUp(self):
        if self.state in [STATE_WAIT_SIGNUP, STATE_SHOW_LOGIN,
                          STATE_SIGNUP_FAIL_USERNAME, STATE_SIGNUP_FAIL_EMAIL,
                          STATE_SIGNUP_FAIL_PASSWORD, STATE_SIGNUP_FAIL_PASSWORD_UNMATCHED]:
            self.state = STATE_SHOW_SIGNUP
            return True
        return False

    def SendSignUp(self, username, email, password, password_confirm):
        if self.state == STATE_SHOW_SIGNUP:
            username = re.sub(" ", "", username)
            email = re.sub(" ", "", email)
            password = re.sub(" ", "", password)
            password_confirm = re.sub(" ", "", password_confirm)
            if username != "" and email != "" and password != "" and password_confirm != "":
                self.login_name = email
                self.login_password = password
                self.state = STATE_WAIT_SIGNUP
                msg = uttt_messages.SignUpMsg(
                    username, email, password, password_confirm)
                return uttt_messages.Serialize(msg)
        return ""

    def SetSignupStatus(self, username_valid, email_valid, password_state):
        if self.state == STATE_WAIT_SIGNUP:
            if username_valid and email_valid and password_state == uttt_messages.PASSWORD_VALID:
                self.state = STATE_SIGNUP_OK
            else:
                if not username_valid:
                    self.state = STATE_SIGNUP_FAIL_USERNAME
                elif not email_valid:
                    self.state = STATE_SIGNUP_FAIL_EMAIL
                elif password_state == uttt_messages.PASSWORD_INVALID:
                    self.state = STATE_SIGNUP_FAIL_PASSWORD
                elif password_state == uttt_messages.PASSWORD_UNMATCHED:
                    self.state = STATE_SIGNUP_FAIL_PASSWORD_UNMATCHED
                else:
                    self.state = STATE_ERROR
                self.login_name = ""
                self.login_password = ""
            return True
        return False

    def SetOtherPlayer(self, player_name):
        self.other_name = player_name
        return True

    def SetUpdateFinished(self):
        if self.state == STATE_WAIT_GAME or self.state == STATE_WAIT_TURN:
            self.state = STATE_SHOW_GAME
        return True

    def HandleMessage(self, msg):
        typeName = msg.GetTypeName()
        retmsg = ""
        if typeName == uttt_messages.PingMsg.GTypeName:
            print "Received Ping"
            retmsg = uttt_messages.Serialize(PongMsg())
        elif typeName == uttt_messages.PongMsg.GTypeName:
            print "Received Pong"
        elif typeName == uttt_messages.BoardStateMsg.GTypeName:
            self.SetBoardOwner(msg.GetBoard(), msg.GetPlayer())
            if g_debug:
                print "Received BoardState"
        elif typeName == uttt_messages.MarkerMsg.GTypeName:
            self.SetBoardMarker(
                msg.GetBoard(), msg.GetPosition(), msg.GetPlayer())
            if g_debug:
                print "Received Marker"
        elif typeName == uttt_messages.NextTurnMsg.GTypeName:
            self.SetNextTurn(msg.GetBoard(), msg.GetPlayer())
            if g_debug:
                print "Received NextTurn"
        elif typeName == uttt_messages.WinStateMsg.GTypeName:
            self.SetWinner(msg.GetPlayer())
            if g_debug:
                print "Received WinState"
        elif typeName == uttt_messages.YouAreMsg.GTypeName:
            self.SetThisPlayer(msg.GetPlayer(), msg.GetPlayerName())
            if g_debug:
                print "Received YouAre"
        elif typeName == uttt_messages.TurnFailedMsg.GTypeName:
            self.SetTurnFailed()
            if g_debug:
                print "Received TurnFailed"
        elif typeName == uttt_messages.LoginReplyMsg.GTypeName:
            self.SetLoginStatus(msg.GetValid())
            if g_debug:
                print "Received LoginReply"
        elif typeName == uttt_messages.SignUpReplyMsg.GTypeName:
            self.SetSignupStatus(
                msg.GetUsernameValid(), msg.GetEmailValid(), msg.GetPasswordState())
            if g_debug:
                print "Received SignUpReply"
        elif typeName == uttt_messages.OpponentNameMsg.GTypeName:
            self.SetOtherPlayer(msg.GetPlayerName())
            if g_debug:
                print "Received OpponentName"
        elif typeName == uttt_messages.UpdateFinishedMsg.GTypeName:
            self.SetUpdateFinished()
            if g_debug:
                print "Received UpdateFinished"
        else:
            print "Unknown Message Type:", typeName, str(msg)

        # self.Display()
        return retmsg
