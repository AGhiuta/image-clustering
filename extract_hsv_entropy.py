#!/usr/bin/env python

import sys
import numpy as np
import urllib
import cv2
import base64
import math
import shelve

"""
compute the hsv histogram (for all three channels)
and the entropy of the image
"""

def extract_hsv_entropy(input_db_name, output_db_name):

	input_db = shelve.open(input_db_name)
	output_db = shelve.open(output_db_name, 'c')

	for key in input_db:
		entropy = 0

		try:
			url = input_db[key]['url']
			req = urllib.urlopen(url)
			arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
			im = cv2.imdecode(arr, -1)
				
			width, height, depth = im.shape
			imsize = width * height

			hsv_im 	= cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
			hist 	= cv2.calcHist([hsv_im], [0, 1, 2], None, [16, 4, 4], [0, 180, 0, 256, 0, 256])

			if hist is None:
				continue

			hist.flags.writeable = True

			"""
			normalize the histogram and compute the entropy
			"""

			for x in range(16):
				for y in range(4):
					for z in range(4):
						hist[x][y][z] /= float(imsize)

						if hist[x][y][z] != 0:
							entropy += hist[x][y][z] * math.log(hist[x][y][z], 2)

			output_db[key] = {'index':input_db[key]['index'], 'url':input_db[key]['url'], \
			'histo':[str(hist.dtype), base64.b64encode(hist), hist.shape], 'entropy':-entropy}

		except:
			pass

	input_db.close()
	output_db.close()

if __name__ == "__main__":
	extract_hsv_entropy(sys.argv[1], sys.argv[2])