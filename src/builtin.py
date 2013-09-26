import json
from collections import namedtuple

import actions
import ECA_parser

import fm

# events = { 'bar' }

def init(arg):
	pass

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
	"int" : ( 1, fm.fcall1(int)),
	"float" : ( 1, fm.fcall1(float)),
	# "long" : ( 1, fm.fcall1(long)), INCOMPLETE
	"str" : ( 1, fm.fcall1(str)),
	"print" : ( 1, fm.fcall1(print))
}

ECA_parser.functions.update( builtin_functions )
