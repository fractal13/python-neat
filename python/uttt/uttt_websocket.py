import websocket
import uttt_data
import uttt_messages
import threading
import Queue

g_debug = False


class UTTTWebSocketApp(websocket.WebSocketApp):

    def connect(self, sockopt=None, sslopt=None):
        if self.sock:
            raise websocket.WebSocketException("socket is already opened")

        self.sock = websocket.WebSocket(
            self.get_mask_key, sockopt=sockopt, sslopt=sslopt)
        self.sock.connect(self.url, header=self.header)
        self._callback(self.on_open)

        return

    def run_forever(self, sockopt=None, sslopt=None, ping_interval=0):
        """
        run event loop for WebSocket framework.
        This loop is infinite loop and is alive during websocket is available.
        sockopt: values for socket.setsockopt.
                        sockopt must be tuple and each element is argument of sock.setscokopt.
        sslopt: ssl socket optional dict.
        ping_interval: automatically send "ping" command every specified period(second)
                        if set to 0, not send automatically.
        """
        if sockopt is None:
            sockopt = []
        if sslopt is None:
            sslopt = {}
        thread = None

        try:
            if not self.sock:
                self.sock = websocket.WebSocket(
                    self.get_mask_key, sockopt=sockopt, sslopt=sslopt)
                self.sock.connect(self.url, header=self.header)
                self._callback(self.on_open)

            if ping_interval:
                thread = threading.Thread(
                    target=self._send_ping, args=(ping_interval,))
                thread.setDaemon(True)
                thread.start()

            while self.keep_running:
                data = self.sock.recv()
                if data is None:
                    break
                self._callback(self.on_message, data)
        except Exception, e:
            self._callback(self.on_error, e)
        finally:
            if thread:
                thread.join()
            self.sock.close()
            self._callback(self.on_close)
            self.sock = None


def uttt_websocket_on_message(ws, message):
    if g_debug:
        print "received text: %s" % (message, )
    msg = uttt_messages.Deserialize(message)
    if g_debug:
        print "translated to msg: %s" % (str(msg), )
    ws.uttt_data.HandleMessage(msg)
    if g_debug:
        print "Handled message."
    return


def uttt_websocket_on_error(ws, error):
    ws.uttt_data.SetState(uttt_data.STATE_SOCKET_ERROR)
    print "Error: ", error
    return


def uttt_websocket_on_close(ws):
    ws.uttt_data.SetState(uttt_data.STATE_SOCKET_CLOSED)
    print "closed"
    return


def uttt_websocket_on_open(ws):
    # ws.uttt_data.SetState(uttt_data.STATE_SOCKET_OPEN)
    print "opened"
    return


def uttt_websocket_create():
    # set up websocket
    # websocket.enableTrace(True)
    ws = UTTTWebSocketApp("ws://rookie.cs.dixie.edu:3334/",
                          on_message=uttt_websocket_on_message,
                          on_error=uttt_websocket_on_error,
                          on_close=uttt_websocket_on_close)
    ws.on_open = uttt_websocket_on_open
    ws.connect()
    return ws


def uttt_send_queue_loop(ws):
    print "uttt_send_queue_loop() Start"
    while ws.keep_running and ws.sock:
        # block for 1 second intervals, to allow for shutdown.
        try:
            text = ws.send_queue.get(True, 1)
            if text:
                if text == "QUIT":
                    ws.keep_running = False
                    ws.sock.close()
                    print "uttt_send_queue_loop() Quitting"
                else:
                    print "uttt_send_queue_loop: send:", text
                    ws.send(text)
        except Queue.Empty as e:
            # print "uttt_send_queue_loop: no data:", ws.keep_running, ws.sock
            pass
    print "uttt_send_queue_loop() Done"
    return


def uttt_websocket_main(data, send_queue):
    ws = uttt_websocket_create()

    # set up game data
    ws.uttt_data = data
    ws.send_queue = send_queue

    t = threading.Thread(target=uttt_send_queue_loop, args=(ws, ))
    t.start()

    # run the websocket loop
    ws.run_forever()
    print "ws.run_forever() done."
    t.join()
    print "send_queue done."
    return
