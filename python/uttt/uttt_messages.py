class IMsg:

    def __init__(self, name):
        self.name = name
        return

    def Serialize(self):
        return str(self)

    def Deserialize(self, parts):
        if len(parts) != 1:
            return False
        return True

    def GetTypeName(self):
        return self.name

    def SetTypeName(self, name):
        self.name = name
        return

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)


class PingMsg(IMsg):

    GTypeName = "ping"

    def __init__(self):
        IMsg.__init__(self, self.GTypeName)
        return


class PongMsg(IMsg):

    GTypeName = "pong"

    def __init__(self):
        IMsg.__init__(self, self.GTypeName)
        return


class BoardStateMsg(IMsg):

    GTypeName = "boardstate"

    def __init__(self, player="N", board=-1):
        IMsg.__init__(self, self.GTypeName)
        self.player = player
        self.board = board
        return

    def Deserialize(self, parts):
        if len(parts) != 3:
            return False
        self.player = str(parts[1])[0]
        self.board = int(parts[2])
        return True

    def GetPlayer(self):
        return self.player

    def GetBoard(self):
        return self.board

    def __str__(self):
        return "%s %s %s" % (str(self.name), str(self.player), str(self.board))


class MarkerMsg(IMsg):

    GTypeName = "marker"

    def __init__(self, player="N", board=-1, position=-1):
        IMsg.__init__(self, self.GTypeName)
        self.player = player
        self.board = board
        self.position = position
        return

    def Deserialize(self, parts):
        if len(parts) != 4:
            return False
        self.player = str(parts[1])[0]
        self.board = int(parts[2])
        self.position = int(parts[3])
        return True

    def GetPlayer(self):
        return self.player

    def GetBoard(self):
        return self.board

    def GetPosition(self):
        return self.position

    def __str__(self):
        return "%s %s %s %s" % (str(self.name), str(self.player), str(self.board), str(self.position))


class NextTurnMsg(IMsg):

    GTypeName = "nextturn"

    def __init__(self, player="N", board=-1):
        IMsg.__init__(self, self.GTypeName)
        self.player = player
        self.board = board
        return

    def Deserialize(self, parts):
        if len(parts) != 3:
            return False
        self.player = str(parts[1])[0]
        self.board = int(parts[2])
        return True

    def GetPlayer(self):
        return self.player

    def GetBoard(self):
        return self.board

    def __str__(self):
        return "%s %s %s" % (str(self.name), str(self.player), str(self.board))


class TurnMsg(IMsg):

    GTypeName = "turn"

    def __init__(self, player="N", board=-1, position=-1):
        IMsg.__init__(self, self.GTypeName)
        self.player = player
        self.board = board
        self.position = position
        return

    def Deserialize(self, parts):
        if len(parts) != 4:
            return False
        self.player = str(parts[1])[0]
        self.board = int(parts[2])
        self.position = int(parts[3])
        return True

    def GetPlayer(self):
        return self.player

    def GetBoard(self):
        return self.board

    def GetPosition(self):
        return self.position

    def __str__(self):
        return "%s %s %s %s" % (str(self.name), str(self.player), str(self.board), str(self.position))


class UpdateMsg(IMsg):

    GTypeName = "update"

    def __init__(self):
        IMsg.__init__(self, self.GTypeName)
        return


class WhoamiMsg(IMsg):

    GTypeName = "whoami"

    def __init__(self):
        IMsg.__init__(self, self.GTypeName)
        return


class WinStateMsg(IMsg):

    GTypeName = "winstate"

    def __init__(self, player="N"):
        IMsg.__init__(self, self.GTypeName)
        self.player = player
        return

    def Deserialize(self, parts):
        if len(parts) != 2:
            return False
        self.player = str(parts[1])[0]
        return True

    def GetPlayer(self):
        return self.player

    def __str__(self):
        return "%s %s" % (str(self.name), str(self.player))


class YouAreMsg(IMsg):

    GTypeName = "youare"

    def __init__(self, player="N", player_name=""):
        IMsg.__init__(self, self.GTypeName)
        self.player = player
        self.player_name = player_name
        return

    def Deserialize(self, parts):
        if len(parts) != 3:
            return False
        self.player = str(parts[1])[0]
        self.player_name = str(parts[2])
        return True

    def GetPlayer(self):
        return self.player

    def GetPlayerName(self):
        return self.player_name

    def __str__(self):
        return "%s %s %s" % (str(self.name), str(self.player), str(self.player_name))


class TurnFailedMsg(IMsg):

    GTypeName = "turnfailed"

    def __init__(self, player="N", text_message=""):
        IMsg.__init__(self, self.GTypeName)
        self.player = player
        self.text_message = text_message
        return

    def Deserialize(self, parts):
        if len(parts) != 3:
            return False
        self.player = str(parts[1])[0]
        self.text_message = UnreplaceSpaces(str(parts[2]))
        return True

    def GetPlayer(self):
        return self.player

    def GetMessage(self):
        return self.text_message

    def __str__(self):
        return "%s %s %s" % (str(self.name), str(self.player), ReplaceSpaces(str(self.text_message)))


class LoginMsg(IMsg):

    GTypeName = "login"

    def __init__(self, email="", password=""):
        IMsg.__init__(self, self.GTypeName)
        self.email = email
        self.password = password
        return

    def Deserialize(self, parts):
        if len(parts) != 3:
            return False
        self.email = UnreplaceSpaces(str(parts[1]))
        self.password = UnreplaceSpaces(str(parts[2]))
        return True

    def GetEmail(self):
        return self.email

    def GetPassword(self):
        return self.password

    def __str__(self):
        return "%s %s %s" % (str(self.name), ReplaceSpaces(str(self.email)), ReplaceSpaces(str(self.password)))


class LoginReplyMsg(IMsg):

    GTypeName = "loginreply"

    def __init__(self, valid=False, token=""):
        IMsg.__init__(self, self.GTypeName)
        self.valid = valid
        self.token = token
        return

    def Deserialize(self, parts):
        if len(parts) != 3:
            return False
        valid = False
        if str(parts[1]) == "valid":
            valid = True
        elif str(parts[1]) == "invalid":
            valid = False
        else:
            print "ERROR: valid string = %s" % (str(parts[1]), )

        self.valid = valid
        self.token = str(parts[2])
        return True

    def GetValid(self):
        return self.valid

    def GetToken(self):
        return self.token

    def __str__(self):
        if self.valid:
            valid = "valid"
        else:
            valid = "invalid"
        return "%s %s %s" % (str(self.name), str(valid), str(self.token))


class SignUpMsg(IMsg):

    GTypeName = "signup"

    def __init__(self, username="", email="", password="", password_confirm=""):
        IMsg.__init__(self, self.GTypeName)
        self.username = username
        self.email = email
        self.password = password
        self.password_confirm = password_confirm
        return

    def Deserialize(self, parts):
        if len(parts) != 5:
            return False
        self.username = UnreplaceSpaces(str(parts[1]))
        self.email = UnreplaceSpaces(str(parts[2]))
        self.password = UnreplaceSpaces(str(parts[3]))
        self.password_confirm = UnreplaceSpaces(str(parts[4]))
        return True

    def GetUsername(self):
        return self.username

    def GetEmail(self):
        return self.email

    def GetPassword(self):
        return self.password

    def GetPasswordConfirm(self):
        return self.password_confirm

    def __str__(self):
        return "%s %s %s %s %s" % (str(self.name), ReplaceSpaces(str(self.username)), ReplaceSpaces(str(self.email)),
                                   ReplaceSpaces(str(self.password)), ReplaceSpaces(str(self.password_confirm)))

PASSWORD_INVALID = 0
PASSWORD_VALID = 1
PASSWORD_UNMATCHED = 2


class SignUpReplyMsg(IMsg):

    GTypeName = "signupreply"

    def __init__(self, username_valid=False, email_valid=False, password_state=PASSWORD_INVALID):
        IMsg.__init__(self, self.GTypeName)
        self.username_valid = username_valid
        self.email_valid = email_valid
        self.password_state = password_state
        return

    def Deserialize(self, parts):
        if len(parts) != 4:
            return False

        username_valid = False
        if UnreplaceSpaces(str(parts[1])) == "valid":
            username_valid = True
        elif UnreplaceSpaces(str(parts[1])) == "invalid":
            username_valid = False
        else:
            print "ERROR: username_valid string = %s" % (str(parts[1]), )

        email_valid = False
        if UnreplaceSpaces(str(parts[2])) == "valid":
            email_valid = True
        elif UnreplaceSpaces(str(parts[2])) == "invalid":
            email_valid = False
        else:
            print "ERROR: email_valid string = %s" % (str(parts[2]), )

        password_state = PASSWORD_INVALID
        if UnreplaceSpaces(str(parts[3])) == "valid":
            password_state = PASSWORD_VALID
        elif UnreplaceSpaces(str(parts[3])) == "invalid":
            password_state = PASSWORD_INVALID
        elif UnreplaceSpaces(str(parts[3])) == "unmatched":
            password_state = PASSWORD_UNMATCHED
        else:
            print "ERROR: password_state string = %s" % (str(parts[3]), )

        self.username_valid = username_valid
        self.email_valid = email_valid
        self.password_state = password_state
        return True

    def GetUsernameValid(self):
        return self.username_valid

    def GetEmailValid(self):
        return self.email_valid

    def GetPasswordState(self):
        return self.password_state

    def __str__(self):
        if self.username_valid:
            username_valid = "valid"
        else:
            username_valid = "invalid"

        if self.email_valid:
            email_valid = "valid"
        else:
            email_valid = "invalid"

        password_state = PASSWORD_INVALID
        if self.password_state == PASSWORD_INVALID:
            password_state = "invalid"
        elif self.password_state == PASSWORD_VALID:
            password_state = "valid"
        elif self.password_state == PASSWORD_UNMATCHED:
            password_state = "unmatched"
        else:
            print "ERROR: password_state number = %d" % (self.password_state, )

        return "%s %s %s %s" % (str(self.name), username_valid, email_valid, password_state)


class OpponentNameMsg(IMsg):

    GTypeName = "opponentname"

    def __init__(self, player_name=""):
        IMsg.__init__(self, self.GTypeName)
        self.player_name = player_name
        return

    def Deserialize(self, parts):
        if len(parts) != 2:
            return False
        self.player_name = UnreplaceSpaces(str(parts[1]))
        return True

    def GetPlayerName(self):
        return self.player_name

    def __str__(self):
        return "%s %s" % (str(self.name), ReplaceSpaces(str(self.player_name)))


class UpdateFinishedMsg(IMsg):

    GTypeName = "updatefinished"

    def __init__(self):
        IMsg.__init__(self, self.GTypeName)
        return


class ErrorMsg(IMsg):

    GTypeName = "error"

    def __init__(self, error_message):
        IMsg.__init__(self, self.GTypeName)
        self.error_message = error_message
        return

    def Deserialize(self, parts):
        self.error_message += " " + " ".join(parts[1:])
        return

    def GetErrorMessage(self):
        return self.error_message

    def __str__(self):
        return IMsg.__str__(self) + " " + self.error_message


def ReplaceAll(string, pattern, replacement):
    result = "".join([c for c in string])
    done = False
    while not done:
        i = result.find(pattern)
        if i != -1:
            result = result[:i] + replacement + result[i + len(pattern)]
        else:
            done = True
    return result


def ReplaceSpaces(string):
    return ReplaceAll(string, " ", "%20")


def UnreplaceSpaces(string):
    return ReplaceAll(string, "%20", " ")


def Serialize(msg):
    return msg.Serialize()


def Deserialize(string):
    parts = string.split()
    if len(parts) == 0:
        return ErrorMsg("Invalid number of arguments to form a message.")
    typeName = parts[0]

    if typeName == PingMsg.GTypeName:
        msg = PingMsg()
    elif typeName == PongMsg.GTypeName:
        msg = PongMsg()
    elif typeName == BoardStateMsg.GTypeName:
        msg = BoardStateMsg()
    elif typeName == MarkerMsg.GTypeName:
        msg = MarkerMsg()
    elif typeName == NextTurnMsg.GTypeName:
        msg = NextTurnMsg()
    elif typeName == TurnMsg.GTypeName:
        msg = TurnMsg()
    elif typeName == UpdateMsg.GTypeName:
        msg = UpdateMsg()
    elif typeName == WhoamiMsg.GTypeName:
        msg = WhoamiMsg()
    elif typeName == WinStateMsg.GTypeName:
        msg = WinStateMsg()
    elif typeName == YouAreMsg.GTypeName:
        msg = YouAreMsg()
    elif typeName == TurnFailedMsg.GTypeName:
        msg = TurnFailedMsg()
    elif typeName == LoginMsg.GTypeName:
        msg = LoginMsg()
    elif typeName == LoginReplyMsg.GTypeName:
        msg = LoginReplyMsg()
    elif typeName == SignUpMsg.GTypeName:
        msg = SignUpMsg()
    elif typeName == SignUpReplyMsg.GTypeName:
        msg = SignUpReplyMsg()
    elif typeName == OpponentNameMsg.GTypeName:
        msg = OpponentNameMsg()
    elif typeName == UpdateFinishedMsg.GTypeName:
        msg = UpdateFinishedMsg()
    else:
        msg = ErrorMsg("Unknown message type name (%s)." % (typeName,))

    if not msg.Deserialize(parts):
        msg = ErrorMsg(typeName + ".Deserialize() failed: %s" % (string,))

    return msg
