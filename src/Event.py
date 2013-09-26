'''
Created on 22 jul. 2013

@author: flokstra
'''

# The event object. All the data given is 
class Event(object):
		def __init__(self,name='new_tweet',**data):
			self.data = data
			self.data['name'] = name
			self.name = name
			self.engine = None
			
		# Gets a value of the event.
		def get(self,name):
			try:
				return self.data[name]
			except:
				raise Exception('Key "'+name+'" not found in event "'+self.name+'"'+', data='+str(self.data))
				
		# Sets a value of the event and returns the value.
		def set(self,name,value):
			self.data[name] = value
			return self.data[name]

		def set_engine(self,engine):
			self.engine = engine

		def get_engine(self):
			return self.engine

emptyEvent = Event('_empty')
initializeEvent = Event('initialize')
finalizeEvent = Event('finalize')

