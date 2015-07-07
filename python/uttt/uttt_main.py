from uttt_gtk import uttt_gtk_main  # windows likes this to be first, I don't know why
import sys
import getopt
from multiprocessing import Process, Queue
from multiprocessing.managers import BaseManager
from threading import Thread
from uttt_data import UTTTData
from uttt_websocket import uttt_websocket_main, uttt_websocket_create
from uttt_cli import uttt_cli_main
from uttt_pygame import uttt_pygame_main
from uttt_ai import uttt_ai_main

if sys.platform == 'win32':
    import multiprocessing.reduction		# make sockets pickable/inheritable

# make game data accessible to all processes


class UTTTDataManager(BaseManager):
    pass

UTTTDataManager.register("UTTTData", UTTTData)


g_short_opts = 'hu:p:a:l:nr:g:t:'
g_long_opts = ["help", "username=", "password=", "ai=", "ai-level=", "no-gui", "results-file=", "genome-file=",
               "ai-type=" ]


def usage(argv):
    print "usage: %s %s %s" % (argv[0], g_short_opts, g_long_opts)


def parse_args(argv):
    arguments = {'username':	 '',
                 'password': '',
                 'ai': 'no',  # 'full', 'displaydriven'
                 'ai-level': 7,
                 'no-gui': False,
                 'results-file': "results.txt",
                 'genome-file': "genome.txt",
                 'ai-type': "minimax",  # 'genome', 'genomelearn'
                 }
    try:
        opts, args = getopt.getopt(argv[1:], g_short_opts, g_long_opts)
    except getopt.GetoptError, err:
        print str(err)
        usage(argv)
        sys.exit(1)

    for o, a in opts:
        if o in ("-u", "--username"):
            arguments['username'] = a
        elif o in ("-p", "--password"):
            arguments['password'] = a
        elif o in ("-a", "--ai"):
            arguments['ai'] = a
        elif o in ("-l", "--ai-level"):
            arguments['ai-level'] = int(a)
        elif o in ("-n", "--no-gui"):
            arguments['no-gui'] = True
            arguments['ai'] = 'full'
        elif o in ("-r", "--results-file"):
            arguments['results-file'] = a
        elif o in ("-g", "--genome-file"):
            arguments['genome-file'] = a
        elif o in ("-t", "--ai-type"):
            arguments['ai-type'] = a
        elif o in ("-h", "--help"):
            usage(argv)
            sys.exit(1)
        else:
            assert False, "Unhandled option: '%s:%s'" % (o, a)

    return arguments

def game_display(data):
    for row in range(9):
        if row % 3 == 0:
            print "+-------+-------+-------+"
        line = ""
        for col in range(9):
            if col % 3 == 0:
                line += "| "
            b = 3 * (row / 3) + (col / 3)
            p = 3 * (row % 3) + (col % 3)
            m = data.GetMarker(b, p)
            line += str(m) + " "
        print line + "|"
    print "+-------+-------+-------+"
    print
    print "Next:", data.GetNextPlayer(), "	", data.GetNextBoard()
    print "Winner", data.GetWinner()
    owners = [ data.GetBoardOwner(b) for b in range(9) ]
    print "Owners:", " ".join(owners)
    print "Me:", data.GetPlayer(), data.GetPlayerName()
    print "You:", data.GetOpponentName()
    print "State:", data.GetState(), data.GetLoggedIn()
    print
    return True

def main(argv):
    print "argv=(%s)" % (argv, )
    arguments = parse_args(argv)
    print "arguments=(%s)" % (str(arguments), )

    # A Queue of messages to send to the web socket
    send_queue = Queue()
    # A Queue of messages to send/receive to/from the ai
    ai_send_queue = Queue()
    ai_recv_queue = Queue()

    # make game data accessible to all processes
    uttt_data_manager = UTTTDataManager()
    uttt_data_manager.start()
    data = uttt_data_manager.UTTTData()

    # start processes
    processes = []

    # websocket receiver
    t = Process(target=uttt_websocket_main, args=(data, send_queue))
    t.start()
    processes.append(t)

    send_queue.put("ping")

    if arguments['username'] and arguments['password']:
        text = data.SendLogin(arguments['username'], arguments['password'])
        send_queue.put(text)

    # command line interface
    # u = Thread(target=uttt_cli_main, args=(data, send_queue))
    # u.start()
    # processes.append(u)

    # pygame interface
    if not arguments['no-gui']:
        v = Process(target=uttt_pygame_main, args=(
            data, send_queue, arguments['ai'], arguments['ai-level'], ai_send_queue, ai_recv_queue))
        v.start()
        processes.append(v)
    else:
        v = None

    # pygtk interface
    if (arguments['ai'] == 'no') and (not arguments['no-gui']):
        print "GTK startup will be delayed 20 seconds due to dbus not working in a separate process."
        w = Process(target=uttt_gtk_main, args=(data, send_queue))
        w.start()
        processes.append(w)
    else:
        w = None

    # ai process
    if arguments['ai'] != 'no':
        x = Process(target=uttt_ai_main, args=(data, send_queue, ai_send_queue,
                                               ai_recv_queue, arguments['no-gui'], arguments['ai-level'],
                                               arguments['results-file'], arguments['genome-file'],
                                               arguments['ai-type'],
                                               arguments['ai']))
        x.start()
        processes.append(x)
    else:
        x = None

    # wait for end of processes
    if t:
        t.join()
        print "websocket joined."
    # u.join()
    if v:
        v.join()
        print "pygame joined."
    if w:
        w.join()
        print "gtk joined."
    if x:
        x.join()
        print "ai joined."
    game_display(data)
    return

if __name__ == "__main__":
    main(sys.argv)
    
