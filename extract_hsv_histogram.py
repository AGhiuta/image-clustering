#!/usr/bin/env python

import cv2
import urllib
import numpy as np
import json
from collections import defaultdict
import base64
import shelve
import sys

"""
extract the color histogram for a given number of images in the HSV color model
(only the Hue and Saturation channels) and save it to a local database
"""
def extract_hsv_histogram(input_db, output_db, n):
	
	for key in input_db:
		try:
			url = input_db[key]
			req = urllib.urlopen(url)
			arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
			im = cv2.imdecode(arr, -1)

			if im is None:
				continue

			hsv_im = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
			hist = cv2.calcHist([hsv_im], [0, 1], None, [50, 60], [0, 180, 0, 256])

			if hist is None:
				continue

			cv2.normalize(hist, hist, cv2.NORM_MINMAX)

			output_db[key] = {'url':url, 'histogram':[str(hist.dtype), base64.b64encode(hist), hist.shape]}

			n -= 1

			if n == 0:
				break

		except:
			pass

if __name__ == '__main__':

	"""
	sys.argv[1] = the input database (contains urls of images)
	sys.argv[2] = the output database; will contain the hsv histograms
	sys.argv[3] = the number of images to be considered for histogram extraction
	"""

	try:
		input_db = shelve.open(sys.argv[1])
		output_db = shelve.open(sys.argv[2], 'c')

		extract_hsv_histogram(input_db, output_db, int(sys.argv[3]))

		input_db.close()
		output_db.close()
	
	except:
		print 'Usage: ./extract_hsv_histogram.py <input_db> <output_db> <n>'