import socket
import struct
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 10000)
sock.bind(server_address)
sock.listen(1)

unpacker = struct.Struct('I 2s f')

while True:
    print >>sys.stderr, '\nwaiting for a connection'
    connection, client_address = sock.accept()
    try:
        data = connection.recv(unpacker.size)

        unpacked_data = unpacker.unpack(data)
        print >>sys.stderr, 'unpacked:', unpacked_data

    finally:
        connection.close()

class MatchServer():
    def __init__(self, port=10000, conn_queue_size=1):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('localhost', port))
        sock.listen(conn_queue_size)
        self.match_list

    def run():
        while True:
            connection, client_address = sock.accept()
            print >>sys.stderr, 'client connected', client_address
            try:
                data = connection.recv(1024)

            finally:
                connection.close()
