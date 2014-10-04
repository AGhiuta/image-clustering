#!/usr/bin/env python

import sys
import urllib
import numpy as np
import scipy
import cv2
import cv
import random
from collections import defaultdict
from collections import OrderedDict
from collections import Counter
from operator import itemgetter
import math
import base64
import json
import copy
from process_kw import *
import shelve

"""
compute the distance between two images based on their hue values
"""

def get_dist(H1, H2):

	sumH2 = 0.0
	sumMinH1H2 = 0.0
 	C1 = Counter(H1)
 	C2 = Counter(H2)
 	count = sum((C1 & C2).values())

 	return 1.0 - float(count) / float(len(H2))

"""
read the data
"""

def read(filename, n):
	items = {}
	index = 0

	input_db = shelve.open(filename)

	for key in input_db:
		try:
			hue = input_db[key]['hue']
			items[input_db[key]['url']] = hue

			index += 1

			if index == n:
				break

		except:
			pass

	input_db.close()

	return items

"""
compute the clusters in each iteration
"""

def compute_clusters(items, centro):
	clusters 	= defaultdict(list)
	j 			= 0

	for item in items:
		v 			= items[item]
		minDist		= 1.1		# used with histogram correlation method
		index 		= 0
		minIndex 	= -1

		for c in centro:
			dist = get_dist(v, c)

			if dist < minDist:
				minDist 	= dist
				minIndex 	= index

			index += 1

		if minIndex >= 0:
			clusters[minIndex].append([minDist, item, v])

	return clusters

"""
reevaluate the centroids after each iteration
"""

def reevaluate_centroids(clusters, old_centro):
	new_centro 	= []
	keys 		= sorted(clusters.keys())

	for key in keys:

		c = clusters[key]

		if len(c) > 0:
			out = []
			d = np.zeros((9, 6), dtype=np.int)

			for item in c:
				hue = item[2]
				for i in range(len(hue)):
					h = hue[i]
					d[i][h] += 1

			out = np.argmax(d, axis=1)

			new_centro.append(tuple(out))

	return new_centro

"""
k-means++ method for centroids initialization
"""

def init_centroids(items, n, K):
	centro 	= []
	np.random.seed(0)
	index 	= np.random.randint(n)
	keys 	= items.keys()

	centro.append(tuple(items[keys[index]]))

	for k in range(1, K):
		D2 			= scipy.array([min([get_dist(c, items[i]) for c in centro]) for i in items], dtype=float)
		probs		= D2 / D2.sum()
		cumprobs 	= probs.cumsum()
		r 			= scipy.rand()

		for j, p in enumerate(cumprobs):
			if r < p:
				index = j
				break

		centro.append(tuple(items[keys[index]]))
	
	return centro

"""
check if the centroids have converged between two successive iterations
"""

def has_converged(old_centro, new_centro):
	n = len(list(set(old_centro) & set(new_centro)))

	if n == len(old_centro) or n == len(new_centro):
		return True

	return False

def save_clusters(centroids, clusters):


	clusters_db = shelve.open("hue_clusters.db", 'c')

	for i in range(len(clusters)):
		clusters[i].sort(key=itemgetter(0))
		c = clusters[i]
		
		clusters_db[str(i)] = c

	clusters_db.close()

def kmeans(items, n, k):
	centro 		= init_centroids(items, n, k)
	s 			= 0
	episodes	= 0
	total		= 50

	while True:
		clusters 	= compute_clusters(items, centro)
		old_centro	= centro
		centro 		= reevaluate_centroids(clusters, centro)

		if has_converged(old_centro, centro) or episodes == total:
			return centro, clusters

		episodes += 1

if __name__ == "__main__":
	n 		= int(sys.argv[2])
	items 	= read(sys.argv[1], n)

	centroids, clusters = kmeans(items, n, int(math.sqrt(n) + math.sqrt(n / 2)))

	print_clus(centroids, clusters)