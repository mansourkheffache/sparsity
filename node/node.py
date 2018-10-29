#!/usr/bin/python3


import numpy as np
import xmlrpc.client
import sys
from xmlrpc.server import SimpleXMLRPCServer

from threading import Thread
import socket
import uuid

import sqlite3
import os


# TODO side stuff to move to utils.py
# just threads, but join() has a return value -- useful for this use case

# class used for multi-threading, might be neeed later
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


class Node:

	def __init__(self, address, port, tracker):
		# X:	dimensionality
		# N:	number of addresses
		# T:	threshold
		# C:	bounds

		self.ip = address
		self.port = port
		self.tracker = tracker

		# connect to tracker
		self.join()

		# init
		self._init_storage()

		self.bins = np.zeros((self.params['N'], self.params['X']), dtype=int)
		# self.addresses = np.random.randint(2, size=(self.params['N'], self.params['X']))


	def _init_storage(self):
		# init db
		# TODO where should I delete?
		# os.remove('./db/' + self.id + '.db')
		conn = sqlite3.connect('db/' + self.id + '.db')
		self.db_cursor = conn.cursor()
		self.db_cursor.execute('CREATE TABLE bins(id INTEGER PRIMARY KEY AUTOINCREMENT, data BLOB)')

		# generate addresses
		self.addresses = np.random.randint(2, size=(self.params['N'], self.params['X']))
		self.storage_addresses = [-1] * self.params['N']

		zeros = np.zeros(shape=self.params['X'])

		for i in range(self.params['N']):
			self.db_cursor.execute("INSERT INTO bins(data) values(?)", (zeros.tobytes(),))
			self.storage_addresses[i] = self.db_cursor.lastrowid



	def _set(self, data):
		# get matching locations
		distances = np.count_nonzero(np.array(data, dtype=int) != self.addresses, axis=1)
		locations = np.where(distances <= self.params['T'])[0]

		# store data into designated locations	
		bipolar_data = np.array(data, dtype=int) * 2 - 1

		for l in locations:
			# TODO parallelize?

			# load bins
			self.db_cursor.execute('SELECT * FROM bins WHERE id=?', (str(self.storage_addresses[l]),))
			bins = np.copy(np.frombuffer(self.db_cursor.fetchone()[1], dtype=int))

			# update bins
			bins += bipolar_data
			bins[bins < -self.params['C']] = -self.params['C']
			bins[bins > self.params['C']] = self.params['C']

			# store bins
			self.db_cursor.execute('UPDATE bins SET data=? WHERE id=?', (bins.tobytes(), str(self.storage_addresses[l])))

		return len(locations)


	def _get(self, address):

		# get matching locations
		distances = np.count_nonzero(np.array(address, dtype=int) != self.addresses, axis=1)
		locations = np.where(distances <= self.params['T'])[0]

		v = np.zeros(shape=self.params['X'], dtype=int)
		for l in locations:
			# TODO parallelize?
			# load bins
			self.db_cursor.execute('SELECT * FROM bins WHERE id=?', (str(self.storage_addresses[l]),))
			bins = np.copy(np.frombuffer(self.db_cursor.fetchone()[1], dtype=int))

			v += bins

		return v

	def _get_recipients(self, origin):

		# turn all to numpy world
		# neighbors_ids = np.array([ int(n['id'], 16) for n in self.neighbors ], dtype=int) 		# needed??
		node_id = int(self.id, 16)
		origin_id = int(origin, 16)

		# distance = index + 1
		index = int(np.log2(node_id ^ origin_id))

		# HACK filters out all None elements - no neighbors at that distance
		return list(filter(None, self.neighbors[:index]))


	def hello(self, peer_details):
		print('[' + self.id + '] HELLO  --  ' + peer_details['id'])

		index = int(np.log2(int(self.id, 16) ^ int(peer_details['id'], 16)))

		self.neighbors[index] = peer_details

		return index


	def join(self):
		with xmlrpc.client.ServerProxy('http://' + self.tracker + '/') as proxy:
			self.id, self.neighbors, self.params = proxy.register(self.ip, self.port)

		peer_details = { 'id': self.id, 'ip': self.ip, 'port': self.port }
		print('PEER ID: ' + self.id)
		for n in filter(None, self.neighbors):
			with xmlrpc.client.ServerProxy('http://' + n['ip'] + ':' + str(n['port']) + '/') as proxy:
				index = proxy.hello(peer_details)

				# TODO compare index to make sure it was inserted in the right place, maybe?


	def store(self, data, origin):
		print('[' + self.id + '] STORE  --  ' + origin)


		# !!! MULTI-THREADED !!!
		# threads = []
		# count = 0

		# # local
		# t = BThread(target=self._set, args=(data,))
		# threads.append(t)
		# t.start()

		# # remote
		# for r in self._get_recipients(origin):
		# 	with xmlrpc.client.ServerProxy('http://' + r['ip'] + ':' + str(r['port']) + '/') as proxy:
		# 		t = BThread(target=proxy.store, args=(data, self.id))
		# 		threads.append(t)
		# 		t.start()

		# # print(len(threads))

		# # TODO do you need string encode/decode??
		# # wait
		# for t in threads:
		# 	count += t.join()

		# return count


		count = 0

		# local
		count += self._set(data)

		# remote
		for r in self._get_recipients(origin):
			with xmlrpc.client.ServerProxy('http://' + r['ip'] + ':' + str(r['port']) + '/') as proxy:
				count += proxy.store(data, self.id)

		return count


	def retrieve(self, address, origin):
		print('[' + self.id + '] RETRIEVE  --  ' + origin)

		# !!! MULTI-THREADED !!!
		# threads = []
		# v = np.zeros(self.X, dtype=int)

		# # local
		# t = BThread(target=self._get, args=(address,))
		# threads.append(t)
		# t.start()

		# # remote
		# for r in self._get_recipients(origin):
		# 	with xmlrpc.client.ServerProxy('http://' + r['ip'] + ':' + str(r['port']) + '/') as proxy:
		# 		t = BThread(target=proxy.retrieve, args=(address, self.id))
		# 		threads.append(t)
		# 		t.start()



		# # TODO do you need string encode/decode??
		# # Nej

		# # wait
		# for t in threads:
		# 	v += t.join()

		# return v.tolist()

		v = np.zeros(self.params['X'], dtype=int)

		# local
		v += self._get(address)

		# remote
		for r in self._get_recipients(origin):
			with xmlrpc.client.ServerProxy('http://' + r['ip'] + ':' + str(r['port']) + '/') as proxy:
				v += np.array(proxy.retrieve(address, self.id), dtype=int)

		return v.tolist()


	def print_info(self):
		print(self.addresses)
		print(self.bins)

		return 0

	def connect(self):
		print('>> Client connection')
		return self.params['X']



if __name__ == "__main__":


	ADDRESS, PORT = get_address()
	TRACKER_ADDRESS = sys.argv[1]

	# start XML-RPC server
	server = SimpleXMLRPCServer((ADDRESS, int(PORT)), use_builtin_types=True, allow_none=True)

	server.register_instance(Node(ADDRESS, PORT, TRACKER_ADDRESS))
	print('Node running on localhost port ' + str(PORT))
	try:
		server.serve_forever()
	except KeyboardInterrupt:
		print("\nKeyboard interrupt received, exiting.")
		sys.exit(0)
