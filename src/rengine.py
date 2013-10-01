# This ECA file parser uses PLY (Python Lex-Yacc)
# Please read http://www.dabeaz.com/ply/ply.html before changing this file.

import imp
import os
import _thread
import threading
import time
import actions
import builtin
import ECA_parser
import Event

import dboffline as dbconnect

# if __name__ == '__main__':
	# import dboffline as dbconnect
# else:
	# import dbconnect
	
engine_thread = None

# A basic observer. It prints the info text to the command line.
class Observer:
	def __init__(self):
		pass
		
	def info(self,data):
		print(data[2])
		
class TwitterEventProducer(object):
	def __init__(self,start_time=None,stop_time=None,speed=60,observer=Observer(),wait=True):
		dbconnect.wait_cache()
		self._speed = speed * 1.0
		self._observer = observer
		self._wait = wait
		if start_time is None:
			self.start_time = dbconnect.times[0]
		else:
			self.start_time = start_time
		if stop_time is None:
			self.stop_time = dbconnect.times[-1]
		else:
			self.stop_time = stop_time
		#
		if dbconnect.wait_cache():
			self._observer.info((True,0,'Waiting for cache to be made.',False))
		if not dbconnect.cache_done:
			self._observer.info((False,0,'Could not get a tweet out of the cache.',False))
		else:
			self._observer.info((True,0,'Cache filled. Rule engine started...',False))
			self.error = None
			self.percent = 0
			self.count = dbconnect.get_start(self.start_time)
			self.stop_index = dbconnect.get_stop(self.stop_time)
			self.time_span = self.stop_time - self.start_time
			self.error = False
			self._stop_event = threading.Event()
		
	def has_next_event(self):
		return self.count < self.stop_index and not self.error
		
	def next_event(self):
		if self._wait:
			if self.count == 0:
				self._stop_event.wait((dbconnect.times[self.count]-self.start_time)/self._speed)
			else:
				self._stop_event.wait((dbconnect.times[self.count]-dbconnect.times[self.count-1])/self._speed)
		tweet = dbconnect.cache[self.count]
		json_dict = builtin.json2objects(tweet[4])
		if json_dict:
			next_event = Event.Event(name='new_tweet',id=tweet[0],text=tweet[1],time=tweet[2],place=tweet[3],json=tweet[4],json_dict=json_dict)
			self.percent = int((dbconnect.times[self.count]-self.start_time) * 99.0 / self.time_span)
			self.count += 1
			return next_event;
		else:
			# no correct json in tweet, silently skip tweet
			self.count += 1
			return self.next_event()

class RuleEngineThread(threading.Thread):
	def __init__(self,start_time=None,stop_time=None,speed=60,observer=Observer(),wait=True,threadsync_event=None):
		threading.Thread.__init__(self)
		self._observer = observer
		self.eventProducer = None
		self.eventProducer = TwitterEventProducer(start_time,stop_time,speed,observer)
		self._stop_event = threading.Event()
		self.produce = None
		self.threadsync_event = threadsync_event
		self.name = "rule_engine_thread"
		
	def stop(self):
		self._stop_event.set()
		
	def stopped(self):
		return self._stop_event.isSet()

	def set_produce_function(self,new_function):
		self.produce = new_function
		
	def handle_single_event(self,event):
		# print('##Handle Event: '+str(event))
		event.set_engine(self)
		# print(str(ECA_parser.ECA_rules))
		for rule in ECA_parser.ECA_rules:
			try:
				if rule.event == event.name:
					if rule.check_event(event):
						try:
							rule.execute(event,self.produce)
						except Exception as e:
							return 'Error\n'+str(e)+'\nIn one of the actions of the ECA rule on line '+str(rule.lineno)
			except Exception as e:
				return 'Error\n'+str(e)+'\nIn the condition of the ECA rule on line '+str(rule.lineno)
		return False

	def add_local_event(self,event):
		print("!!!ADDING EVENT TO RULE ENGINE!!!")
		
	def run(self):
		ECA_parser.restore_vars()
		error = None
		percent = 0
		error = False
		if self.threadsync_event:
			self.threadsync_event.wait()
		if self.stopped():
			self._observer.info((False,percent,'Engine stopped',False))
		else:
                	error = self.handle_single_event(Event.initializeEvent)
		while self.eventProducer.has_next_event() and not self.stopped():
			next_event = self.eventProducer.next_event()
			if  self.threadsync_event:
				self.threadsync_event.wait()
			error = self.handle_single_event(next_event)
			if self.eventProducer.percent > percent:
				percent = self.eventProducer.percent
				self._observer.info((True,percent,'Working... '+str(percent)+'%',False))
		error = self.handle_single_event(Event.finalizeEvent)
		if not self.stopped():
			self._observer.info((False,100,'Done',False))
		elif not error:
			self._observer.info((False,percent,'Engine stopped',False))
		else:
			self._observer.info((False,percent,error,True))
		print('#!Finish rule engine thread, variables are: \n')
		print(ECA_parser.variables)
				
def load_file(filePath):
	if engine_thread and engine_thread.is_alive():
		return 'Stop the rule engine before loading a new file'
	try:
		file = open(filePath).read()+'\n'
	except IOError:
		return 'The file does not exist. Please try again.'
	else:
		try:
			ECA_parser.parse(file)
			return ''
		except Exception as e:
			print("#PARSE ERROR!" + str(e))
			return str(e)

def has_errors():
	return ECA_parser.has_errors()
			
def discard_file():
	if not engine_thread:
		ECA_parser.reset()

def start_rule_engine(start_time=None,stop_time=None,speed=100000,observer=Observer(), produce=None,threadsync_event=None):
	global engine_thread
	if has_errors():
		return "Rule engine not starting because of ECA errors"
	if engine_thread and engine_thread.is_alive():
		return 'Rule engine already running!'
	try:
		engine_thread = RuleEngineThread(start_time,stop_time,speed,observer,True,threadsync_event)
		engine_thread.set_produce_function(produce)
		engine_thread.start()
		# Don't return any value here, as DUI.py will interpret any
		# returned value as an error.
	except Exception as e:
		return 'Rule engine did not start due to an unknown error! ' + str(e)
	return
	
def get_rule_engine():
	return engine_thread

def stop_rule_engine():
	if engine_thread:
		engine_thread.stop()

def debug_produce_function(message):
	decoded = actions.decode(message)
	print('TO-BROWSER: '+str(decoded))

# Test function. Run this file (in interactive mode) to parse the standaard.ECA in the same folder.
if __name__ == '__main__':
	dbconnect.connect_to_db( '130.89.10.35','antwan','batatweets','anton_tweets' )
	#print(load_file(os.path.join(os.getcwd(),'f.ECA')))
	#print(load_file(os.path.join(os.getcwd(),'small.ECA')))
	#print(load_file(os.path.join(os.getcwd(),'standaard.ECA')))
	#print(load_file(os.path.join(os.getcwd(),'mcall.ECA')))
	print(load_file(os.path.join(os.getcwd(),'fourgadgetdemo.ECA')))
	#print(load_file(os.path.join(os.getcwd(),'simple_wordcloud.ECA')))
	#print(load_file(os.path.join(os.getcwd(),'complex_wordcloud.ECA')))
	start_rule_engine(speed=100000000)
	# start_rule_engine(speed=100000000, produce=debug_produce_function)
