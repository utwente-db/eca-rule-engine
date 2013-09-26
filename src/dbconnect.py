from pg8000 import DBAPI
import threading
import traceback
import time
import bisect

cache_done = False
cache_thread = None
db = None
counter = 0

class Observer:
	def __init__(self):
		pass
	
	def info(self,data):
		if isinstance(data,tuple):
			print((data[2]))
		else:
			print(data)
	
observer = Observer()

def connect_to_db( host_input, user_input, password_input, database_input, input_observer=observer):
	global db, cache_thread, observer
	observer = input_observer
	try:
		db = DBAPI.connect(user=user_input,host=host_input,port=5432,database=database_input,password=password_input)
	except Exception as e:
		print("#!DB-LOAD-EXCEPTION: "+str(e))
		traceback.print_exc()
		return False
	else:
		cache_thread = FillCache()
		return True
		
def get_start(time):
	wait_cache()
	return bisect.bisect_left(times,time)
	
def get_stop(time):
	wait_cache()
	return bisect.bisect(times,time)
	
def disconnect():
	wait_cache()
	global cache_thread, cache_done, cache, db, counter
	cache_thread = None
	cache_done = False
	cache = None
	db = None
	counter = 0
	
def get_len_tweets():
	wait_cache()
	return len(cache)
	
class FillCache(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.start()
		
	def run(self):
		global cache, cache_done, times
		try:
			tweets = db.cursor()
			tweets.execute("select * from tweets")
			cache_tuple = tweets.fetchall()
			tweets.close()
		except:
			print("#!DB-LOAD-EXCEPTION: "+str(e))
			traceback.print_exc()
			if observer:
				observer.info('Could not load the tweets from the database. Try reconnecting to the database.')
		else:
			cache = []
			times = []
			for tweet in cache_tuple:
				temp = list(tweet)
				temp[2] = int(time.mktime(time.strptime(temp[2][:19]+temp[2][-5:],"%a %b %d %H:%M:%S %Y")))
				cache.append(temp)
			cache = sorted(cache,key=lambda r: r[2])
			times = [r[2] for r in cache]
			cache_done = True
			db.close()
			if True:
				for t in cache:
					print(t)
					print(",")
			if observer:
				observer.info((None,None,'Cache filled.',False))
			else:
				print('Cache filled.')
		
def wait_cache():
	if cache_thread is not None:
		if cache_thread.is_alive():
			cache_thread.join()
			return True
		else:
			return False
	else:
		raise Exception('Connection not made or closed')
		traceback.print_exc()
		
if __name__ == '__main__':
	connect_to_db( '130.89.10.35','antwan','batatweets','anton_tweets' )
