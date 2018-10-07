
import numpy as np
import random


class Node:

	def __init__(self, X, T, N, C):
		# X:	dimensionality
		# N:	number of addresses
		# T:	threshold

		self.bins = np.zeros((N, X))
		self.threshold = T
		self.addresses = np.random.randint(2, size=(N, X))
		self.bounds = C

	def store(self, data):

		# get matching locations
		distances = np.count_nonzero(data != self.addresses, axis=1)
		locations = np.where(distances <= self.threshold)

		# store data into designated locations	
		bipolar_data = data * 2 - 1
		self.bins[locations] += bipolar_data
		self.bins[self.bins < -self.threshold] = -self.threshold
		self.bins[self.bins > self.threshold] = self.threshold


	def retrieve(self, address):
		# get matching locations
		distances = np.count_nonzero(address != self.addresses, axis=1)
		locations = np.where(distances <= self.threshold)

		# get sum of bins
		v = np.sum(self.bins[locations], axis=0)

		return v
