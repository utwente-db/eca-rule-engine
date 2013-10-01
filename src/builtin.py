import json
from collections import namedtuple
from datetime import tzinfo, timedelta, date, datetime

import actions
import Event
import ECA_parser
import tweetprocessor

import fm

# events = { 'bar' }

def init(arg):
	pass

def run_python(sp):
	try:
		return eval(sp)
	except Exception as e:
		print("WARNING: python("+sp+"): "+str(e))
		return None

def run_import(mod):
	try:
		return __import__(mod)
	except Exception as e:
		print("WARNING: import failed:"+str(e))
		return None

def debug_publish(v):
	tweetprocessor.debug_publish = v
	return v

def get_attribute(obj,attr_name):
	if isinstance(obj, Event.Event):
		# return the Event data value
		return obj.data[attr_name]
	else:
		return obj.__getattribute__(attr_name)
	

def method_call(obj,mn,parlist):
	try:
		if parlist:
			return lambda event: (obj(event)).__getattribute__(mn)(*parlist(event))
		else:
			return lambda event: get_attribute(obj(event),mn)
	except Exception as e:
		print("WARNING: method_call:"+str(e))
		return None

def sqbrktIndex(lambda_expr, lambda_index):
	return lambda event: (lambda_expr(event))[lambda_index(event)]

def if_then_else(lambda_cond, lambda_then, lambda_else):
	return lambda event: lambda_then(event) if lambda_cond(event) else lambda_else(event)

def _bind_and_compute(cname,v,lambda_result,event):
	# this function creates a temporary bind of the cname variable. When
	# there is a nesting there could be a conflict.
	if cname in ECA_parser.tmpvar:
		raise Exception('Variable '+cname+' already exists')
	ECA_parser.tmpvar[cname] = v
	result = lambda_result(event)
	del ECA_parser.tmpvar[cname]
	return result

def forall(cname, lambda_collection, lambda_result):
	return lambda event: [_bind_and_compute(cname,v,lambda_result,event) for v in lambda_collection(event)]

def json_serialize(json):
	# perhaps a bit clumsy?
	return str(json).replace('\'','\"')

def json2objects(data):
	try:
		return json.loads(data)
	except Exception as e:
		# print("WARNING: no json: "+str(e))
		return None

builtin_functions = {
	"json_serialize" : ( 1, fm.fcall1(json_serialize) ),
	"python" : ( 1, fm.fcall1(run_python)),
	"import" : ( 1, fm.fcall1(run_import)),
	"debug_publish" : ( 1, fm.fcall1(debug_publish)),
	"int" : ( 1, fm.fcall1(int)),
	"float" : ( 1, fm.fcall1(float)),
	# "long" : ( 1, fm.fcall1(long)), INCOMPLETE
	"str" : ( 1, fm.fcall1(str)),
	"print" : ( 1, fm.fcall1(print))
}

ECA_parser.functions.update( builtin_functions )
