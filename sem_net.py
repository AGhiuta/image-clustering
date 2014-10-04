#!/usr/bin/env python

import numpy as np
import sys
import json
import base64
import enchant
import inflect
import shelve
from collections import defaultdict

"""
compute a score for every pair of words based on their frequency
"""

def compute_scores(kw_dict, indexes):
	n = len(kw_dict)
	keys = sorted(kw_dict.keys())
	W = np.zeros((n, n), dtype=np.float)
	W[n-1][n-1] = 1.0

	for i in range(n - 1):
		ki = keys[i]
		s = set(indexes[ki])
		W[i][i] = 1.0

		for j in range(i + 1, n):
			kj = keys[j]
			count = len(list(s & set(indexes[kj])))
			W[i][j] = float(count) / float(kw_dict[ki])
			W[j][i] = float(count) / float(kw_dict[kj])

	return W

if __name__ == "__main__":

	kw_dict = {}
	kwords = {}
	indexes = defaultdict(list)
	d = enchant.Dict('en_US')
	p = inflect.engine()
	colors = ['black', 'blue', 'brown', 'cyan', 'gray', 'green', 'indigo', 'magenta', 'pink', 'purple', 'red', 'silver', 'turquoise', 'violet', 'white', 'yellow']
	total_kw = 0
	count = 0

	input_db = shelve.open(sys.argv[1])
	output_db = shelve.open(sys.argv[2], 'c')

	"""
	process the keywords of each image
	"""

	for key in input_db:
		try:
			kw = input_db[key]['keywords'].split(',')
			tmp = {} 

			for i in range(len(kw)):
				k = kw[i].lower()

				try:
					if p.singular_noun(k) != False:
						k = p.singular_noun(k)
				except:
					pass

				if len(k) > 0:
					if not d.check(k):
						s = d.suggest(k)
						
						if len(s) > 0:
							k = d.suggest(k)[0]

					"""
					remove the colors because they have a high frequency, but are not important
					as they carry no relevant information (e.g. white background)
					"""

					if k not in colors:
						tmp[k] 	= k
						kw_dict[k] = kw_dict.get(k, 0) + 1

						indexes[k].append(int(input_db[key]['index']))

			kw = tmp.values()
			count += 1
			total_kw += len(kw)


			"""
			save the newly processed words
			"""
			output_db[key] = {'url':input_db[key]['url'], 'index':input_db[key]['index'], 'keywords':kw}

		except:
			print kw

	W = compute_scores(kw_dict, indexes)

	"""
	save the score
	"""
	scores_db = shelve.open(sys.argv[3], 'c')
	scores_db['sem_net'] = {'dict':kw_dict, 'score':[str(W.dtype), base64.b64encode(W), W.shape]}

	input_db.close()
	output_db.close()
	scores_db.close()