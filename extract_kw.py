#!/usr/bin/env python

import redis
import json
import sys
import shelve

def extract_kw(redis_host, input_db_name, output_db_name):

	r = redis.StrictRedis(host=redis_host, port=6379, db=0)

	input_db = shelve.open(input_db_name)
	output_db = shelve.open(output_db_name, 'c')

	for key in input_db:
			i = int(input_db[key]['index'])
			item = r.lindex('dreamstime:items', i)
			j = json.loads(item)

			output_db[key] = {'index':input_db[key]['index'], 'url':input_db[key]['url'], 'keywords':j['keywords']}

	input_db.close()
	output_db.close()

if __name__ == "__main__":
	extract_kw(sys.argv[1], sys.argv[2], sys.argv[3])