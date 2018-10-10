#!/usr/bin/python3


import uuid
import numpy as np
from xmlrpc.server import SimpleXMLRPCServer
import sys

class Tracker():
	# TODO watch for ids with trailing 0's


	def __init__(self, space):
		self.active_peers = {}
		self.space = space

	def register(self, ip, port):

		# create entry
		hex_id = hex(np.random.randint(2**self.space))[2:]
		peer_details = { 'ip': ip, 'port': port, 'id': hex_id }

		neighbors = self.get_neighbors(hex_id)


		# add to list of active peers
		self.active_peers[hex_id] = peer_details

		print(peer_details)

		return hex_id, neighbors

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
				neighbors[i] = self.active_peers[hex(matches[np.random.randint(len(matches))])[2:]]
			except ValueError:
				# no matches, most likely
				neighbors[i] = None

		return neighbors

	def get_active_peers(self):
		return self.active_peers



if __name__ == "__main__":

	# start XML-RPC server
	with SimpleXMLRPCServer(('localhost', 8000), use_builtin_types=True, allow_none=True) as server:
		server.register_instance(Tracker(20))
		print('Tracker running on localhost port 8000')
		try:
			server.serve_forever()
		except KeyboardInterrupt:
			print("\nKeyboard interrupt received, exiting.")
			sys.exit(0)