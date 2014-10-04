#!/usr/bin/env python

import sys
import numpy as np
import urllib
import cv2
import shelve

"""
compute the average color saturation of an image
"""

def extract_saturation(input_db_name, output_db_name):

	input_db = shelve.open(input_db_name)
	output_db = shelve.open(output_db_name, 'c')

	for key in input_db:
		try:
			url = input_db[key]['url']
			req = urllib.urlopen(url)
			arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
			im 	= cv2.imdecode(arr, -1)
				
			width, height, depth = im.shape
			imsize = width * height

			hsv_im 	= cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
			sat 	= cv2.split(hsv_im)[1]

			val = float(np.sum(sat)) / float(imsize)

			output_db[key] = {'index':input_db[key]['index'], 'url':input_db[key]['url'], 'saturation':val}

		except:
			pass

	input_db.close()
	output_db.close()

if __name__ == "__main__":
	extract_saturation(sys.argv[1], sys.argv[2])