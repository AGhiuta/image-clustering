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
import kmeans_hue
import kmeans_hsv_entro
from process_kw import *
from datetime import datetime
import pylab
import psutil
import shelve

"""
compute the distance between two images
"""

def get_dist(a, b, W, indexes):

	c1 = Counter(a)
	c2 = Counter(b)

	n = sum((c1 & c2).values())

	return 1.0 - float(n) / float(len(b))

"""
read the semantic network
"""

def read_sem_net(filename):
	input_db = shelve.open(filename)

	for key in input_db:
		try:
			dtype 	= np.dtype(input_db[key]['score'][0])
			W 		= np.frombuffer(base64.decodestring(input_db[key]['score'][1]), dtype)
			W 		= W.reshape(input_db[key]['score'][2])

			return W, input_db[key]['dict']
		except:
			pass

"""
compute the clusters in each iteration
"""

def compute_clusters(items, centro, W, indexes):
	clusters 	= defaultdict(list)
	j 			= 0

	for item in items:				#iterate through the input set
		v 			= items[item]
		minDist		= 1.1
		index 		= 0
		minIndex 	= -1

		for c in centro:			# for each centroid
			dist = get_dist(v, c, W, indexes)

			if dist < minDist:		# chose the closest centroid
				minDist 	= dist
				minIndex 	= index

			index += 1

		if minIndex >= 0:
			clusters[minIndex].append([minDist, item, v])	#append the sample to the corresponding cluster

	return clusters

"""
reevaluate the centroids after each iteration
"""

def reevaluate_centroids(clusters, old_centro, kwords):
	new_centro	= []
	keys = sorted(clusters.keys())

	for key in keys:

		c = clusters[key]
		if len(c) > 0:
			data = {}

			for i in range(len(c)):
				kw = c[i][2]

				for k in kw:
					data[k] = data.get(k, 0) + 1

			new_centro.append(OrderedDict(sorted(data.items(), key=itemgetter(1), reverse=True)).keys()[:42])

	return new_centro

"""
initialize the centroids
"""

def init_centroids(items, n, K, W, indexes):

	index 	= random.sample(range(n), K)
	keys	= items.keys()
	centro 	= []

	for i in index:
		centro.append(items[keys[i]])

	return centro

"""
verify if the clusters converged between two successive iterations
"""

def has_converged(old_centro, new_centro):
	
	for i in range(len(old_centro)):
		n = len(set(old_centro[i]) & set(new_centro[i]))
		if(n != len(old_centro[i])):
			return False

	return True 

"""
save the clusters and the corresponding centroinds
"""

def save_clusters(centroids, clusters, W, indexes):

	clusters_db = shelve.open('clusters.db', 'c')
	centroids_db = shelve.open('centroids.db', 'c')

	for i in range(len(clusters)):
		clusters[i].sort(key=itemgetter(0))
		c = clusters[i]
		clusters_db[str(i)] = c

	for i in range(len(centroids)):
		centroids_db[str(i)] = centroids[i]

	clusters_db.close()
	centroids_db.close()

"""
compute the distances from each image in a cluster to the center of
that cluster and come up with an error value
"""

def get_error(centroids, clusters, W, indexes, n):
	e 		= 0.0
	dists 	= []
	for i in range(len(clusters)):
		c 		= clusters[i]
		centro 	= centroids[i]
		s 		= 0.0

		for item in c:
			d = get_dist(centro, item[2], W, indexes)
			e += d
			s += d
		
		dists.append(s)

	e 	/= float(len(clusters))
	dev = 0.0

	for d in dists:
		dev += (d - e)**2

	return math.sqrt(dev / float(len(clusters)))

"""
the actual k-means clustering algorithm
"""

def kmeans(items, n, k, W, indexes, kwords):

	centro 		= init_centroids(items, n, k, W, indexes)
	s 			= 0
	episodes	= 0
	total		= 50

	while True:
		clusters 	= compute_clusters(items, centro, W, indexes)
		old_centro	= centro
		centro 		= reevaluate_centroids(clusters, centro, kwords)

		if has_converged(old_centro, centro) or episodes == total:
			return centro, clusters

		episodes += 1

"""
read the average color saturation for each image
"""

def read_saturation(filename):
	sat = {}
	input_db = shelve.open(filename)

	for key in input_db:
			try:
				s = int(input_db[key]['saturation'])
				sat[input_db[key]['url']] = s
			except:
				pass

	input_db.close()

	return sat

def kmeans_h(centro, clusters, data):
	new_centro 	= []
	new_clus	= []

	index = 0

	for key in clusters:

		c 		= clusters[key]
		items 	= {}

		if len(c) > 0:

			for item in c:
				items[item[1]] = data[item[1]]

			n = len(items)
			k = int(round(math.sqrt(n)))

			inner_centro, inner_clus = kmeans_hue.kmeans(items, n, k)

			for i in range(len(inner_centro)):
				new_centro.append(copy.copy(centro[index]))
				new_centro[len(new_centro) - 1] += inner_centro[i]

			for item in sorted(inner_clus.keys()):
				new_clus.append(inner_clus[item])

		index += 1

	return new_centro, new_clus

"""
split each clusters into 2 new clusters according to the saturation
of the images in the original clusters and a treshold value for that
saturation
"""

def split_clusters(centro, clusters, sat):
	n = len(clusters)

	treshold = 90

	for i in range(n):
		c = clusters[i]
		m = len(clusters)
		sat_inf = 0
		sat_sup	= 0
		tot_inf = 0
		tot_sup = 0

		for item in c:

			if sat[item[1]] < treshold:
				sat_inf += sat[item[1]]
				tot_inf += 1

				try:
					clusters[m].append(item)
				except:
					clusters.append([item])
			else:
				sat_sup += sat[item[1]]
				tot_sup += 1

		if tot_inf > 0:
			centro.append(copy.copy(centro[i]))
			try:
				centro[m].append(sat_inf / tot_inf)
			except:
				centro.append([sat_inf / tot_inf])

		if tot_sup > 0:
			centro[i].append(sat_sup / tot_sup)
		
		try:
			for item in clusters[m]:
				if item in clusters[i]:
					clusters[i].remove(item)
		except:
			pass

	return centro, clusters

if __name__ == "__main__":
	p, i = read_kw(sys.argv[3])			# lists of keywords for pictures & illustrations
	W, kwords = read_sem_net(sys.argv[4])		# semantic network scores & dictionary of words (with their frequencies)
	k = int(sys.argv[2])				# number of clusters
	n = int(sys.argv[1])				# number of images to be clustered
	items = dict(p.items() + i.items())
	indexes = {}							# the intedex of the words in the dictionary
	keys = sorted(kwords.keys())

	hues = kmeans_hue.read(sys.argv[5], 10000)
	sat = read_saturation(sys.argv[6])

	times = {}

	for j in range(len(keys)):
		indexes[keys[j]] = j

	for item in items:
		kw 	= items[item]
		s = {}

		for w in kw:
			s[w] = kwords[w]

		items[item] = OrderedDict(sorted(s.items(), key=itemgetter(1), reverse=True)).keys()[:42]

	data = dict(items.items()[:n])

	centro, clusters = kmeans(data, n, k, W, indexes, kwords)
	centro, clusters = split_clusters(centro, clusters, sat)
	centro, clusters = kmeans_h(centro, clusters, hues)

	save_clusters(centro, clusters, W, indexes)