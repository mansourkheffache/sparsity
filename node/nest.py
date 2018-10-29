#!/usr/bin/python3

import subprocess
import sys
import signal
import time
import threading
import socket
from xmlrpc.server import SimpleXMLRPCServer
from node import Node




def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def spawn_node(port):

	PORT = port

	# start XML-RPC server
	server = SimpleXMLRPCServer((ADDRESS, int(PORT)), use_builtin_types=True, allow_none=True)

	server.register_instance(Node(ADDRESS, PORT, TRACKER_ADDRESS))
	print('-- Node running on ' + ADDRESS + ':' + str(PORT))

	server.serve_forever()


# params
n = int(sys.argv[1])
ADDRESS = get_ip()
TRACKER_ADDRESS = sys.argv[2]

# container for processes
threads = []


for i in range(n):
	t = threading.Thread(target=spawn_node, args=(5000 + i,))
	threads.append(t)
	t.start()



def signal_handler(signal, frame):
    print('Shutting down...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
print('Nest running...')
forever = threading.Event()
forever.wait()
