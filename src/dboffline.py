import time

#topic = None
topic = 'batavierenrace'
#topic = 'sports'
#topic = 'sr11'
#topic = 'weer'
#topic = 'p2000'
#topic = 'xfactor'

if topic == 'sr11':
	from sr11_offline_tweets import cache
elif topic == 'batavierenrace':
	from bata_offline_tweets import cache
elif topic == 'sports':
	from sports_offline_tweets import cache
elif topic == 'sr11':
	from sr11_offline_tweets import cache
elif topic == 'weer':
	from weer_offline_tweets import cache
elif topic == 'p2000':
	from p2000_offline_tweets import cache
elif topic == 'xfactor':
	from xfactor_offline_tweets import cache
else:
	from offline_tweets import cache

cache = sorted(cache,key=lambda r: r[2])
import bisect
times = [r[2] for r in cache]

counter = 0
cache_done = True

class Observer:
	def __init__(self):
		pass
	
	def info(self,data):
		print((data[2]))
	
observer = Observer()

def connect_to_db( host_input, user_input, password_input, database_input, input_observer=observer):
	return True
	
def get_start(time):
	return bisect.bisect_left(times,time)
	
def get_stop(time):
	return bisect.bisect(times,time)
	
def disconnect():
	global counter
	counter = 0
	
def get_len_tweets():
	return len(cache)
	
def wait_cache():
	return False
	
if __name__ == '__main__':
	connect_to_db( '130.89.10.35','antwan','batatweets','anton_tweets' )
