import socket
import struct
import sys
from ClientNetworking import *
from MatchClient import MatchClient

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 10000)
sock.connect(server_address)

client = MatchClient(sock)
