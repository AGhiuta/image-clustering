#!/usr/bin/env python

import cv2
import urllib
import numpy as np
import shelve
import sys

"""
extract the surf descriptors from an image given by its url address
"""

def extract_surf(url):

	try:
		req = urllib.urlopen(url)
		arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
		im = cv2.imdecode(arr, -1)

		if im is None:
			return None, None

		surf = cv2.SURF(400)
		kp, des = surf.detectAndCompute(im, None)

		return kp, des
	except:
		print 'Error while processing the image.'

if __name__ == '__main__':

	"""
	sys.argv[1] = the input database; contains the images (url, keywords)
	sys.argv[2] = the output database; will contain the surf keypoints & descriptors of images
	sys.argv[3] = the number of images for which the surf descriptors are to be computed
	"""

	try:
		input_db = shelve.open(sys.argv[1])
		output_db = shelve.open(sys.argv[2], 'c')
		n = int(sys.argv[3])

		for key in input_db:
			url = input_db[key]['url']
			kp, des = extract_surf(url)

			if kp is not None and des is not None:
				output_db[key] = {'kp': kp, 'des': des}
				n -= 1

				if n == 0:
					break

		input_db.close()
		output_db.close()
	except:
		print 'Usage: ./extract_surf.py <input_db> <output_db> <n>'