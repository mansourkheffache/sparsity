#!/usr/bin/python3


import numpy as np
import xmlrpc.client
import sys
from xmlrpc.server import SimpleXMLRPCServer

from threading import Thread
import socket
import uuid

# TODO side stuff to move to utils.py
# just threads, but join() has a return value -- useful for this use case
class BThread(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        Thread.__init__(self, group, target, name, args, kwargs, daemon=daemon)

        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self):
        Thread.join(self)
        return self._return

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # TODO change 8.8.8.8 with tracker ??
    s.connect(('8.8.8.8', 80))
    return s.getsockname()[0]


class Node:

	def __init__(self, X, N, T, C, tracker):
		# X:	dimensionality
		# N:	number of addresses
		# T:	threshold
		# C:	bounds

		self.X = X
		self.bins = np.zeros((N, X), dtype=int)
		self.threshold = T
		self.addresses = np.random.randint(2, size=(N, X))
		self.bounds = C
		self.tracker = tracker

		# tmp fix without tracker
		self.neighbors = []
		self.id = uuid.uuid4().hex[:5]


	def _set(self, data):
		# get matching locations
		distances = np.count_nonzero(np.array(data, dtype=int) != self.addresses, axis=1)
		locations = np.where(distances <= self.threshold)[0]

		# store data into designated locations	
		bipolar_data = np.array(data, dtype=int) * 2 - 1
		self.bins[locations] += bipolar_data
		self.bins[self.bins < -self.bounds] = -self.bounds
		self.bins[self.bins > self.bounds] = self.bounds


		return len(locations)


	def _get(self, address):


		# get matching locations
		distances = np.count_nonzero(np.array(address, dtype=int) != self.addresses, axis=1)
		locations = np.where(distances <= self.threshold)

		# get sum of bins
		v = np.sum(self.bins[locations], axis=0)

		return v

	def _get_recipients(self, origin):

		# turn all to numpy world
		# neighbors_ids = np.array([ int(n['id'], 16) for n in self.neighbors ], dtype=int) 		# needed??
		node_id = int(self.id, 16)
		origin_id = int(origin, 16)

		# distance = index + 1
		index = int(np.log2(node_id ^ origin_id))

		# HACK filters out all None elements - no neighbors at that distance
		return filter(None, self.neighbors[:index])


	def join(self):

		with xmlrpc.client.ServerProxy('http://' + self.tracker + '/') as proxy:

			self.id, self.neighbors = proxy.register(get_ip_address, 4420)


	def store(self, data, origin):

		threads = []
		count = 0

		# local
		t = BThread(target=self._set, args=(data,))
		threads.append(t)
		t.start()

		# remote
		for r in self._get_recipients(origin):
			with xmlrpc.client.ServerProxy('http://' + r['ip'] + ':' + r['port'] + '/') as proxy:
				t = BThread(target=proxy.store, args=(data, self.id))
				threads.append(t)
				t.start()

		# TODO do you need string encode/decode??
		# wait
		for t in threads:
			count += t.join()

		return count


	def retrieve(self, address, origin):

		threads = []
		v = np.zeros(self.X, dtype=int)

		# local
		t = BThread(target=self._get, args=(address,))
		threads.append(t)
		t.start()

		# remote
		for r in self._get_recipients(origin):
			with xmlrpc.client.ServerProxy('http://' + r['ip'] + ':' + r['port'] + '/') as proxy:
				t = BThread(target=proxy.retrieve, args=(address, self.id))
				threads.append(t)
				t.start()



		# TODO do you need string encode/decode??
		# Nej

		# wait
		for t in threads:
			v += t.join()

		return v.tolist()

	def print_info(self):
		print(self.addresses)
		print(self.bins)



if __name__ == "__main__":

	# start XML-RPC server
	with SimpleXMLRPCServer(('localhost', 8000), use_builtin_types=True) as server:
		server.register_instance(Node(20, 10, 8, 5, 'lul'))
		print('Node running on localhost port 8000')
		try:
			server.serve_forever()
		except KeyboardInterrupt:
			print("\nKeyboard interrupt received, exiting.")
			sys.exit(0)
