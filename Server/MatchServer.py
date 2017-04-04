from socket import AF_INET, SOCK_STREAM, socket
from ServerNetworking import *
from Match import Match
from threading import Thread

from sys import stderr
import direct.directbase.DirectStart

class MatchServer():
    def __init__(self, port=10000, conn_queue_size=5):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.bind(('localhost', port))
        self.port = port
        self.socket.listen(conn_queue_size)
        self.running = False
        self.match_list = []
        self.queue = []

    # don't run externally
    def _run(self):
        print "MatchServer started on ", self.port
        while self.running:
            connection, client_address = self.socket.accept()
            print >>stderr, 'client connected', client_address
            try:
                self.queue.append((connection, client_address))
            except:
                pass
            if len(self.queue) == 2:
                match = Match(self.queue[:2], 60.0)
                self.match_list.append(match)
                self.queue = self.queue[2:]
                match.start()


    def run(self):
        print "RUN"
        if not self.running:
            self.running = True
            self._run()

    #def stop(self):
    #    print "Shutting down MatchServer on ", self.port
    #    self.running = False

if __name__ == '__main__':
    m = MatchServer()
    t = Thread(target=m.run)
    t.daemon = True
    t.start()
    run()
