#!/usr/bin/python3

import subprocess
import sys
import signal
import time
import threading
import socket
from xmlrpc.server import SimpleXMLRPCServer

from node import Node


import socketserver

class ThreadedXMLRPCServer(socketserver.ThreadingMixIn, SimpleXMLRPCServer):
	pass


# GET IP ADDRESS AND PORT
def get_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
        PORT = s.getsockname()[1]
    except:
        IP = '127.0.0.1'
        PORT = 6969
    finally:
        s.close()

    return IP, PORT



def spawn_node():

	ADDRESS, PORT = get_address()

	# start XML-RPC server
	server = ThreadedXMLRPCServer((ADDRESS, int(PORT)), use_builtin_types=True, allow_none=True)

	server.register_instance(Node(ADDRESS, PORT, TRACKER_ADDRESS))
	print('-- Node running on ' + ADDRESS + ':' + str(PORT))

	server.serve_forever()


# params
n = int(sys.argv[1])
TRACKER_ADDRESS = sys.argv[2]

# container for processes
threads = []


for i in range(n):
	t = threading.Thread(target=spawn_node, args=())
	threads.append(t)
	t.start()


print('Nest running...')

