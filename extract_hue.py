#!/usr/bin/env python

import redis
import json
import sys
import numpy as np
import urllib
import cv2
import base64
import math
import shelve

def extract_hue(input_db_name, output_db_name):

	input_db = shelve.open(input_db_name)
	output_db = shelve.open(output_db_name, 'c')

	for key in input_db:
		try:
			item = input_db[key]
			url = item['url']
			req = urllib.urlopen(url)
			arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
			im 	= cv2.imdecode(arr, -1)
				
			width, height, depth = im.shape
			imsize = width * height

			hsv_im 	= cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
			hist 	= cv2.calcHist([hsv_im], [0], None, [16], [0, 180])

			if hist is None:
				continue

			hist.flags.writeable = True

			for x in range(16):
				hist[x] /= float(imsize)

			output_db[key] = {'index':item['index'], 'url':item['url'], 'histogram':[str(hist.dtype), base64.b64encode(hist), hist.shape]}

		except:
			pass

	input_db.close()
	output_db.close()

if __name__ == "__main__":
	extract_hue(sys.argv[1], sys.argv[2])