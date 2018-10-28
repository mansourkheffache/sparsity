#!/usr/bin/python3


import uuid
import numpy as np
from xmlrpc.server import SimpleXMLRPCServer
import random
import sys


# GET IP ADDRESS
import socket
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


class Tracker():
	# TODO watch for ids with trailing 0's


	def __init__(self, addr_space, X, N, T, C):
		self.active_peers = {}
		# TODO space is different from X
		self.space = addr_space
		self.params = { 'X': X, 'N': N, 'T': T, 'C': C}

	def register(self, ip, port):

		# create entry
		hex_id = hex(np.random.randint(2**self.space))[2:]
		peer_details = { 'ip': ip, 'port': port, 'id': hex_id }

		neighbors = self.get_neighbors(hex_id)


		# add to list of active peers
		self.active_peers[hex_id] = peer_details

		print(peer_details)

		return hex_id, neighbors, self.params

	def get_neighbors(self, id):

		# get neighbors
		other_peers = np.array([int(k, 16) for k in self.active_peers.keys()], dtype=int)
		peer_id = int(id, 16)

		# NB: distances 0 -> 19
		distances = np.floor(np.log2(peer_id ^ other_peers))

		neighbors = [None] * self.space
		for i in range(self.space):
			matches = other_peers[distances == i]
			try:

				# FIX bad coding
				neighbors[i] = self.active_peers[hex(random.choice(matches))[2:]]				# slicing removes 0x from hex string

			except IndexError:
				# no matches, most likely
				neighbors[i] = None

		return neighbors

	def get_active_peers(self):
		return self.active_peers





if __name__ == "__main__":

	# start XML-RPC server
	# QUESTION	maybe need to use ip and not localhost?
	server = SimpleXMLRPCServer((get_ip(), 8000), use_builtin_types=True, allow_none=True)

	S = int(sys.argv[1])
	X = int(sys.argv[2])
	N = int(sys.argv[3])
	T = int(sys.argv[4])
	C = int(sys.argv[5])

	server.register_instance(Tracker(S, X, N, T, C))
	print('Tracker running on ' + get_ip() + ' port 8000')
	try:
		server.serve_forever()
	except KeyboardInterrupt:
		print("\nKeyboard interrupt received, exiting.")
		sys.exit(0)