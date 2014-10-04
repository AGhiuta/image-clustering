#!/usr/bin/env python

import numpy as np
import sys
import cv2
import cv
import random
import copy
import math
import urllib
import json
import base64
import pylab
import shelve

from learning_rate import *
from radius import *
from neighbourhood import *
from collections import defaultdict
from process_kw import *
from datetime import datetime
from memory_profiler import profile

"""
compute the distance between two images based on
their hsv histograms and entropies
"""

def get_dist(W, v):

	sumH1 = 0.0
	sumH2 = 0.0
	sumMinH1H2 = 0.0
	H1 = W[0]
	H2 = v[0]
	E1 = min(W[1], v[1])
	E2 = max(W[1], v[1])

	for x in range(16):
		for y in range(4):
			for z in range(4):
				valH1 = H1[x][y][z]
				valH2 = H2[x][y][z]
				sumMinH1H2 += min(valH1, valH2)
				sumH2 += valH2
 
	distH1H2 = 1.0 - float(sumMinH1H2) / float(sumH2)
	distE1E2 = 1.0 - math.fabs(E1 / E2)

	p = 0.0

	if distE1E2 < 0.2:
		p = 0.1
	elif distE1E2 < 0.4:
		p = 0.2
	elif distE1E2 < 0.6:
		p = 0.3
	elif distE1E2 < 0.8:
		p = 0.4
	else:
		p = 0.5

	return (1.0 - p) * distH1H2 + p * distE1E2

"""
read the hsv histogram and the entropy from the input database
"""

@profile
def read(filename, n):
	items = {}
	index = 0

	input_db = shelve.open(filename)

	for key in input_db:
		try:
			dtype = np.dtype(input_db[key]['histogram'][0])
			hist = np.frombuffer(base64.decodestring(input_db[key]['histogram'][1]), dtype)
			hist = hist.reshape(input_db[key]['histogram'][2])

			items[input_db[key]['url']] = [hist, input_db[key]['entropy']]
			index += 1

			if index == n:
				break

		except:
			pass

	input_db.close()

	return items

"""
initialize the neurons of the network with random values
"""

@profile
def init_neurons(items, n, K):
	
	index = random.sample(range(n), K**2)
	item = items[items.keys()[0]]
	keys = items.keys()
	W = np.empty((K, K), dtype=object)
	k = 0

	for i in range(K):
		for j in range(K):
			W[i][j] = items[keys[k]]
			W[i][j][0].flags.writeable = True

			for x in range(16):
				for y in range(4):
					for z in range(4):
						W[i][j][0][x][y][z] *= random.random()

			W[i][j][1] *= random.random()

			k += 1

	return W
	
"""
perform the actual classification with the self organizing map method
"""

@profile
def som_classification(input_db_name, output_db_name, n, k):
	np.random.seed()

	items = read(input_db_name, n)
	output_db = shelve.open(output_db_name, 'c')
	times = {}
	shape = items[items.keys()[0]][0].shape
	k = int(round(math.sqrt(math.sqrt(n))))
	W = init_neurons(items, n, k)
	clusters = defaultdict(list)
	t = 0
	iter_count = 10000
	keys = items.keys()

	for t in range(iter_count):
		index = random.randint(0, n - 1)
		l_rate = learning_rate(t, iter_count)
		v = items[keys[index]]
		minDist = 1.1
		xmin = -1
		ymin = -1

		"""
		find the closest neuron to the current image (histogram & entropy stored in v)
		"""

		for i in range(k):
			for j in range(k):
				dist = get_dist(W[i][j], v)

				if dist < minDist:
					minDist = dist
					xmin 	= j
					ymin 	= i

		"""
		update the values stored by the neurons
		"""

		for i in range(16):
			for j in range(4):
				for l in range(4):
					W[ymin][xmin][0][i][j][l] += l_rate * (v[0][i][j][l] - W[ymin][xmin][0][i][j][l])

		W[ymin][xmin][1] += l_rate * (v[1] - W[ymin][xmin][1])

	t = 0

	"""
	compute the clusters and store them locally
	"""

	for item in items:
		v 		= items[item]
		minDist = 1.1
		xmin 	= -1
		ymin 	= -1

		for i in range(k):
			for j in range(k):
				dist = get_dist(W[i][j], v)

				if dist < minDist:
					minDist = dist
					xmin 	= j
					ymin 	= i

		key = int(ymin) * k + int(xmin)

		clusters[key].append([item, v])

	for key in clusters:
		c = clusters[key]
		output_db[key] = clusters[key]

	output_db.close()

if __name__ == "__main__":
	som_classification(sys.argv[1], sys.argv[2], int(sys.argv[3]), 8)