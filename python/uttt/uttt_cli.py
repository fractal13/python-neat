import sys
import uttt_messages


def uttt_cli_main(data, send_queue):
    while True:
        data.Display()
        print """
commands:
        1- ping 2- pong
        3- quit
        4- turn       5- update 6- whoami
        7- login      8- signup
"""
        xstr = raw_input("cmd? ")
        try:
            x = int(xstr)
        except:
            x = 0

        try:
            msg = None
            if x == 1:
                msg = uttt_messages.PingMsg()
                send_queue.put(uttt_messages.Serialize(msg))
            elif x == 2:
                msg = uttt_messages.PongMsg()
                send_queue.put(uttt_messages.Serialize(msg))
            elif x == 3:
                break
            elif x == 4:
                board = input("board? ")
                position = input("position? ")
                text = data.SendTurn(board, position)
                send_queue.put(text)
            elif x == 5:
                text = data.SendUpdate()
                send_queue.put(text)
            elif x == 6:
                text = data.SendWhoami()
                send_queue.put(text)
            elif x == 7:
                email = raw_input("email? ")
                password = raw_input("password? ")
                text = data.SendLogin(email, password)
                send_queue.put(text)
            elif x == 8:
                username = raw_input("username? ")
                email = raw_input("email? ")
                password = raw_input("password? ")
                confirm = raw_input("password? ")
                text = data.SendSignUp(username, email, password, confirm)
                send_queue.put(text)
            else:
                print "Unknown command"
        except AttributeError as e:
            print "AttributeError:", str(e)
        except:
            print "Unexpected error:", sys.exc_info()[0]

    return
