#!/usr/bin/env python

import sys
import shelve

"""
read the keywords and separate the images into 'pictures' and 'illustrations'
"""

def read_kw(filename):
	pics = {}
	illustrations = {}
	input_db = shelve.open(filename)

	for key in input_db:
		try:
			kw 	= input_db[key]['keywords']

			if 'illustration' in kw or 'cartoon' in kw:
				illustrations[input_db[key]['url']] = kw
			else:
				pics[input_db[key]['url']] = kw
		except:
			pass

	return pics, illustrations

if __name__ == "__main__":
	p, i = read_kw(sys.argv[1])