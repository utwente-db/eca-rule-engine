import ply.yacc as yacc
import imp
import os
import sys
import logging
import traceback
import copy
import actions
import Event
import ECA_parser_lex
from ECA_parser_lex import tokens, lexer

# To prevent modules from loading multiple times the modules are saved in a dictionary
modules = {}

events = []
variables = {}
tmpvar    = {}
constants = {}
ECA_rules = []
functions = {}

# import the standard functions from the actions module
functions.update( actions.action_functions )

# This is the class representing the ECA rules. Make a new ECA rule by using the following code:
# new_ECARule = ECARule('name of event',expression_condition,[expression_actions],line number of the rule)
class ECARule(object):
	def __init__(self,name,event,condition,action,lineno):
		self.name = name
		self.event = event
		self.condition = condition
		self.action = action
		self.lineno = lineno
	
	def __str__(self):
		return 'Name of event: '+str(self.event)+'\nThe conditions are:\n'+\
		str(self.condition) + '\nThe actions are:\n'+str(self.action)
		
	def is_system():
		return event.startswith('_')

	def check_event(self,event):
		try:
			return self.condition(event)
		except Exception as e:
			print('Condition failed: ' + str(e))
			print(str(self))
			traceback.print_exc()
			#sys.exit(0)
			print("CONTINUING.....")
		
	def execute(self,event,produce):
		for expression in self.action:
			try:
				res = expression(event)
			except Exception as e:
				print('Action failed: ' + str(e))
				print(str(self))
				traceback.print_exc()
				#sys.exit(0)
			if (produce != None and res != None and actions.is_action(res)):
				produce(res)

visualization_setup_rule = None
			
# calls t_error() in the lexer
def t_error(t):
    ECA_parser_lex.t_error(t)

########## YACC

# indicates which tokens will be parsed first.
precedence = (
	('left', 'IN'),
	('left', 'OR'),
	('left', 'AND'),
	('left', 'NOT'),
	('left', 'COMPARE'),
	('left', 'PLUS', 'MINUS', 'MODULO'),
	('left', 'POINT'),
	('left', 'TIMDIV')
)

# The start symbol
def p_ecafile(p):
	'''ecafile	: import
				| constant
				| declaration
				| ecarule
				| NEWLINE
				| import ecafile
				| celldef ecafile
				| constant ecafile
				| declaration ecafile
				| ecarule ecafile
				| NEWLINE ecafile'''
	pass
	
# Imports a module if it's not yet imported and the adds it to the modules dictionary. The event names and variables are added to the variables in this file. TODO import more things
def p_ecafile_import(p):
	'''import : IMPORT CNAME NEWLINE'''
	try:
		if p[2] not in modules:
			modules[p[2]] = imp.load_source('module.'+p[2],os.path.join(os.getcwd(),'modules',p[2]+'.py'))
	except ImportError as e:
		raise Exception('Module "'+p[2]+'" not found in line '+str(p.lineno(2)));
	else:
		try:
			modules[p[2]].init(globals())
		except Exception as e:
			print(('error',e))

# Describes a CELL definitions
def p_ecafile_celldef(p):
	'''celldef	: CELL stringval GADGET stringval OPTIONS dictvalue NEWLINE
				| CELL stringval dictvalue NEWLINE'''
	global visualization_setup_rule
	if len(p)==8:
		celldef = actions.cell_definition(p[2],p[4],p[6])
	else:
		celldef = actions.raw_cell_definition(p[2],p[3])
	visualization_setup_rule.action.append(celldef)
		
# Sets a constant if the given name is not yet taken
def p_ecafile_constant(p):
	'''constant	: CONSTANT CNAME EQUALS expression NEWLINE'''
	if p[2] not in constants and p[2] not in variables and p[2] not in functions and p[2].split('.',1)[0] not in events:
		constants[p[2]] = p[4](None)
	else:
		raise Exception('The name of "'+p[2]+'" is already taken. Line '+str(p.lineno(2)))
		
# Sets a variable if the given name is not yet taken. The value of the variable is None.
def p_ecafile_declaration_cname(p):
	'''declaration	: DECLARE CNAME NEWLINE'''
	if p[2] not in constants and p[2] not in variables and p[2] not in functions and p[2].split('.',1)[0] not in events:
		variables[p[2]] = None
	else:
		raise Exception('The name of "'+p[2]+'" is already taken. Line '+str(p.lineno(2)))
		
# Sets a variable even if it is already a variable. The value equals the given expression.
def p_ecafile_declaration_assign(p):
	'''declaration	: DECLARE assign NEWLINE'''
	p[2](None)
	
# Adds an ECA rule to the list. If the condition is not specified the condition is always True.
def p_opt_rulename(p):
	'''opt_rulename	: RULE CNAME NEWLINE
				| '''
	if len(p) == 1:
		p[0] = 'noname'
	else:
		p[0] = p[2]

# Adds an ECA rule to the list. If the condition is not specified the condition is always True.
def p_ecafile_ecarule(p):
	'''ecarule	: opt_rulename event action
				| opt_rulename event condition action'''
	if len(p) == 4:
		ECA_rules.append(ECARule(p[1],p[2],lambda event: True,p[3],p.lineno(1)))
	else:
		ECA_rules.append(ECARule(p[1],p[2],p[3],p[4],p.lineno(1)))
		
# The event of an ECA rule. Returns the name of the event or raises an error if the event name does not exist.
def p_ecafile_ecarule_event(p):
	'''event : EVENT CNAME newline'''
	if p[2] in events:
		p[0] = p[2]
	else:
		# raise Exception('The name "'+p[2]+'" is no event. Line '+str(p.lineno(2)))
		events.append(p[2])
		p[0] = p[2]
		
# The condition of an ECA rule. Returns the expression.
def p_ecafile_ecarule_condition(p):
	'''condition : CONDITION expression newline'''
	p[0] = p[2]
	
# The action of an ECA rule. Returns the list of calls.
def p_ecafile_ecarule_action(p):
	'''action	: ACTION calls'''
	p[0] = p[2]
	

# The statements of the action can either be an assignment or an expression
def p_ecafile_ecarule_action_statement(p):
	'''action_statement	: expression
				| assign'''
	p[0] = p[1]

# The calls of the action. Returns a list with all following expressions divided by a newline.
def p_ecafile_ecarule_action_calls(p):
	'''calls	: action_statement newline
				| action_statement newline calls'''
	p[0] = [p[1]]
	if len(p) == 4:
		p[0] += p[3]

def p_methodcall(p):
	'''expression : expression POINT CNAME LPAREN expressionlist RPAREN
				| expression POINT CNAME LPAREN RPAREN
				| expression POINT CNAME'''
	if len(p) == 7:
		p[0] = builtin.method_call(p[1],p[3],get_list(p[5]))
	elif len(p) == 6:
		p[0] = builtin.method_call(p[1],p[3],lambda event: [])
	else:
		p[0] = builtin.method_call(p[1],p[3],None)

# A function. If the function is in the functions dictionary the function is called with a tuple, where the first value equals the name of the function and the second item is a function returning the list of expressions found between the parentheses.
def p_function(p):
	'''expression : CNAME LPAREN expressionlist RPAREN
				| CNAME LPAREN RPAREN'''
	if len(p)==5:
		narg = len(p[3])
	else:
		narg = 0
	if p[1] in functions:
		if functions[p[1]][0] != narg:
			raise Exception('Arity function call: '+p[1] + '(#arg='+str(functions[p[1]][0])+') incorrect: '+str(len(p[3])))
		if len(p)==5:
			p[0] = functions[p[1]][1]((p[1],get_list(p[3])))
		else:
			p[0] = functions[p[1]][1]((p[1],[]))
	else:
		raise Exception('Function not specified: '+p[1] + '()')
		
# Returns a list of expressions.
def p_function_expression_list(p):
	'''expressionlist	: expression
						| expression COMMA expressionlist'''
	p[0] = [p[1]]
	if len(p) == 4:
		p[0] += p[3]

# Returns the expression between the parentheses
def p_arrayindex(p):
	'''expression : expression LSBRACK expression RSBRACK'''
	p[0] = builtin.sqbrktIndex(p[1],p[3])
		
# Returns the expression between the parentheses
def p_brackets(p):
	'''expression : LPAREN expression RPAREN'''
	p[0] = p[2]
	
# Returns a function to retrieve the value of the constant, variable or event
def p_cname(p):
	'''expression : CNAME'''
	if p[1] in constants:
		p[0] = (lambda input: lambda event: constants[input])(p[1])
	elif p[1] in tmpvar:
		p[0] = get_tmpvar(p[1])
	elif p[1] in variables:
		p[0] = get_variable(p[1])
	elif p[1].split('.',1)[0] in events:
		p[0] = get_event(p[1])
	else:
		raise Exception('Unknown variable "'+p[1]+'" in line '+str(p.lineno(1)))
		
# Returns a function returning the number. If the number has a dot in it the number returned is a float
def p_number(p):
	'''expression	: NUMBER'''
	if len(p[1].split('.')) > 1:
		p[0] = (lambda input: lambda event: float(input))(p[1])
	else:
		p[0] = (lambda input: lambda event: int(input))(p[1])
		
# Returns a function returning the negative value of the expression.
def p_negative(p):
	'''expression : MINUS expression'''
	p[0] = (lambda event: - (p[2])(event))
	
# Returns a function returning the string without the quotation marks
def p_string(p):
	'''expression : stringval'''
	p[0] = (lambda input: lambda event: input)(p[1])
	
# Returns a function returning True
def p_true(p):
	'''expression : TRUE'''
	p[0] = lambda event: True
	
# Returns a function returning False
def p_false(p):
	'''expression : FALSE'''
	p[0] = lambda event: False
	
# Returns a function returning None
def p_none(p):
	'''expression : NONE'''
	p[0] = lambda event: None
	
# Returns a function returning a list of (solved) expressions.
def p_list(p):
	'''expression	: LSBRACK listitems RSBRACK
					| LSBRACK RSBRACK'''
	if len(p) == 4:
		p[0] = get_list(p[2])
	else:
		p[0] = get_list(p[2])
		
# Returns a list of expressions.
def p_listitems(p):
	'''listitems	: expression
					| expression COMMA listitems'''
	if len(p) == 2:
		p[0] = [p[1]]
	else:
		p[0] = [p[1]] + p[3]
		
# Returns a function returning a dictionary of (solved) expressions.
def p_dict(p):
	'''expression	: dictvalue'''
	p[0] = p[1]

# Returns a dictionary
def p_dictvalue(p):
	'''dictvalue	: LCBRACK dictitems RCBRACK
					 | LCBRACK RCBRACK'''
	if len(p) == 4:
		p[0] = get_dict(p[2])
	else:
		p[0] = get_dict({})

# The definition of a dictionary tag, can be both a CNAME and a string
def p_dicttag(p):
	'''dicttag	: CNAME
				| stringval'''
	if p[1].startswith('\''):
		p[0] = p[1]
	else:
		p[0] = p[1]
		
# Returns a dictionary
def p_dictitems(p):
	'''dictitems	: dicttag COLON expression
					| dicttag COLON expression COMMA dictitems'''
	if len(p) == 4:
		p[0] = { p[1] : p[3] }
	else:
		p[5].update({p[1] : p[3]})
		p[0] = p[5] 

# Returns the assignment function
def p_newevent_expression(p):
	'''expression	: NEWEVENT CNAME dictvalue'''
	event_name = p[2]
	lambda_dict = p[3] 
	if  event_name not in events:
		# raise Exception('Event "'+p[2]+'" does not exits. Line '+str(p.lineno(1)))
		print('WARNING: Event "'+p[2]+'" does not exits (yet?). Line '+str(p.lineno(1)))
	def add_newevent(event) : 
		newdata = lambda_dict(event)
		if  event_name not in events:
			raise Exception('Event "'+event_name+'" does not exits in events')
		newevent = Event.Event(name=event_name,**newdata)
		event.get_engine().handle_single_event(newevent)
	p[0] = add_newevent

# Returns a function to assign a value to a variable or event.
def p_assign(p):
	'''	assign		: CNAME EQUALS expression
					| CNAME LSBRACK expression RSBRACK EQUALS expression'''
	if p[1] not in constants and p[1].split('.',1)[0] not in events and p[1] not in functions:
		if len(p)==4:
			ass_name = p[1]
			ass_op   = p[2]
			ass_expr = p[3]
			ass_sbscr= None
		else:
			ass_name = p[1]
			ass_op   = p[5]
			ass_expr = p[6]
			ass_sbscr= p[3]
		if ass_op == '=':
			if ass_name not in variables:
				variables[ass_name] = None
			p[0] = assign_variable(ass_name,ass_sbscr,ass_expr)
		elif ass_op == '+=' and ass_name in variables:
			if ass_sbscr:
				raise Exception('assignment += not impl for []')
			p[0] = assign_variable(ass_name,ass_sbscr,lambda event: variables[ass_name] + ass_expr(event))
		elif ass_op == '-=' and ass_name in variables:
			if ass_sbscr:
				raise Exception('assignment -= not impl for []')
			p[0] = assign_variable(ass_name,ass_sbscr,lambda event: variables[ass_name] - ass_expr(event))
		else:
			raise Exception('The variable "'+p[1]+'" has not been declared. Line '+str(p.lineno(1)))
	else:
		raise Exception('The name "'+p[1]+'" is already taken. Line '+str(p.lineno(1)))
		
# Returns a function comparing two expressions
def p_compare(p):
	'''expression	: expression COMPARE expression'''
	if p[2] == '==':
		p[0] = (lambda left, right: lambda event: left(event) == right(event))(p[1],p[3])
	elif p[2] == '<=':
		p[0] = (lambda left, right: lambda event: left(event) <= right(event))(p[1],p[3])
	elif p[2] == '>=':
		p[0] = (lambda left, right: lambda event: left(event) >= right(event))(p[1],p[3])
	elif p[2] == '<':
		p[0] = (lambda left, right: lambda event: left(event) < right(event))(p[1],p[3])
	elif p[2] == '>':
		p[0] = (lambda left, right: lambda event: left(event) > right(event))(p[1],p[3])
	elif p[2] == '!=':
		p[0] = (lambda left, right: lambda event: left(event) != right(event))(p[1],p[3])
		
# Returns a function returning "not expression".
def p_not(p):
	'''expression : NOT expression'''
	expr = p[2]
	p[0] = lambda event: not expr(event)
	
# Returns a function returning "expression or expression"
def p_or(p):
	'''expression : expression OR expression'''
	left = p[1]
	right = p[3]
	p[0] = lambda event: left(event) or right(event)
	
# Returns a function returning "expression and expression"
def p_and(p):
	'''expression : expression AND expression'''
	left = p[1]
	right = p[3]
	p[0] = lambda event: left(event) and right(event)

# Returns a function returning "expression and expression"
def p_in(p):
	'''expression : expression IN expression'''
	left = p[1]
	right = p[3]
	p[0] = lambda event: left(event) in right(event)

# Returns a function returning "expression % expression"
def p_modulo(p):
	'''expression : expression MODULO expression'''
	left = p[1]
	right = p[3]
	p[0] = lambda event: left(event) % right(event)
	
# Returns a function returning "expression + expression" or  "expression - expression"
def p_plus_minus(p):
	'''expression	: expression PLUS expression
					| expression MINUS expression'''
	if p[2] == '+':
		p[0] = (lambda left, right: lambda event: left(event) + right(event))(p[1],p[3])
	else:
		p[0] = (lambda left, right: lambda event: left(event) - right(event))(p[1],p[3])
		
# Returns a function returning "expression * expression" or  "expression / expression"
def p_multi_division(p):
	'''expression : expression TIMDIV expression'''
	if p[2] == '*':
		p[0] = (lambda left, right: lambda event: left(event) * right(event))(p[1],p[3])
	else:
		p[0] = (lambda left, right: lambda event: left(event) / right(event))(p[1],p[3])
		
# INCOMPLETE, introduces 7 shift/reduce's, maybe stick to python syntax
def p_ifthenelse(p):
	'''expression	: IF expression THEN action_statement ELSE action_statement'''
	p[0] = builtin.if_then_else(p[2],p[4],p[6])

# The forall_header is necessary because we need to declare the loop variable
def p_forall_header(p):
	'''forall_header : FORALL CNAME''' 
	create_tmpvar(p[2])
	p[0] = p[2]

# INCOMPLETE, more shift reduces introduced here
def p_forall(p):
	'''expression	: forall_header IN expression COLON action_statement'''
	delete_tmpvar(p[1])
	p[0] = builtin.forall(p[1],p[3],p[5])

# Does nothing with the newlines
def p_stringval(p):
	'''stringval	: STRING'''
	p[0] = p[1][1:-1]

# Does nothing with the newlines
def p_newline(p):
	'''newline	: NEWLINE
				| NEWLINE newline'''
	pass

# Handles the errors in the docement
def p_error(p):
	if p is None:
		raise Exception('Unexpected end of file')
	else:
		if p.type != 'NEWLINE':
			t_error(p)
		else:
			raise Exception('Unexpected newline on line '+str(p.lineno))
		
def create_tmpvar(name):
	tmpvar[name] = 'unused'

def delete_tmpvar(name):
	del tmpvar[name]

# Returns a function returning the value of the variable with the given name
def get_tmpvar(name):
	return lambda event: tmpvar[name]

# Returns a function returning the value of the variable with the given name
def get_variable(name):
	return lambda event: variables[name]
	
# Returns a function assigning a value to a variable with the given name. The function returns the result of the given expression
def assign_variable(name,subscript,function):
	if subscript:
		def av(event):
			(variables[name])[subscript(event)] = function(event)
			return variables[name]
		return av
	else:
		def av(event):
			variables[name] = function(event)
			return variables[name]
		return av
	
# Returns a function which returns the event or gets a attribute of the event.
def get_event(name):
	split_name = name.split('.',1)
	def ge(event):
		if split_name[0] != event.name:
			raise lex.LexError('The given event name did not match the name of the generated event.',' ')
		if len(split_name) > 1:
			return event.get(split_name[1])
		else:
			return event
	return ge
	
# Returns a function assigning a attribute or event to an event.
def assign_event(name,function):
	split_name = name.split('.',1)
	def ae(event):
		if len(split_name) > 1:
			return event.set(split_name[1],function(event))
		else:
			event = function(event)
			return event
	return ae
	
# Returns a function returning a list with the results of the excecuted expressions.
def get_list(list):
	def gl(event):
		new_list = []
		for item in list:
			new_list.append(item(event))
		return new_list
	return gl

# Returns a function returning a dict with the results of the excecuted expressions.
def get_dict(dict):
	def gd(event):
		new_dict = {}
		for item in dict.keys():
			varlambda = dict.get(item)
			new_dict[item] = varlambda(event)
		return new_dict
	return gd

save_variables = {}
	

parse_error = False

# Resets the variables of the eca file
def reset():
	global events, variables, constants, ECA_rules, visualization_setup_rule,  functions
	global lex_error, parse_error
	ECA_parser_lex.lex_error = False
	parse_error = False
	events = ['initialize', 'finalize']
	variables = {}
	tmpvar    = {}
	constants = {}
	ECA_rules = []
	visualization_setup_rule = ECARule('noname','initialize',lambda event: True,[],0)
	ECA_rules.append(visualization_setup_rule)
	new_functions = {
	}
	functions.update( new_functions )

def has_errors():
	global lex_error, parse_error
	return ECA_parser_lex.lex_error or parse_error
	
def parse(string):
	reset()
	lexer.lineno = 1
	lexer.paren = 0
	lexer.sbrack = 0
	logging.basicConfig(filename='log.log',level=logging.DEBUG)
	log = logging.getLogger()
	parser.parse(string,tracking=True,debug=log)
	save_vars()
	
# Saves the initial state of the variables
def save_vars():
	global variables, save_variables
	save_variables = copy.deepcopy(variables)
	
# Restores the initial state of the variables
def restore_vars():
	global variables, save_variables
	if save_variables:
		variables = copy.deepcopy(save_variables)
	
parser = yacc.yacc() # initialize the parser

import builtin # must be here because of circular definition

if __name__ == '__main__':
	parse(open(os.path.join(os.getcwd(),'standaard.ECA')).read())
