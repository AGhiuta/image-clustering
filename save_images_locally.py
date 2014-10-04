import redis
import shelve

"""
	retrieve n images (url, keywords) from a redis server and store them locally
"""

def save_images_locally(r, output_db, n):
	for i in xrange(n):
		tmp = int(r.srandmember('kw:woman'))
		output_db[str(i)] = r.lindex('dreamstime:items', tmp)

if __name__ == '__main__':

	"""
	sys.argv[1] = the redis server host where the images (url, keywords) are stored
	sys.argv[2] = output_db
	sys.argv[3] = the number of images to be retrieved
	"""

	try:
		r = redis.Redis(host=sys.argv[1], port=6379, db=0)
		output_db = shelve.open(sys.argv[2], 'c')
		n = int(sys.argv[3])

		save_images_locally(r, output_db, n)
	except:
		print 'Usage: ./save_images_locally.py <redis server host> <output_db> <n>'