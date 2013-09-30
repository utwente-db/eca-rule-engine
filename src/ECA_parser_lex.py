import ply.lex as lex

## CNAME can be translated to these 
reserved = {
	'AND'		: 'AND',
	'OR'		: 'OR',
	'NOT'		: 'NOT',
	'True'		: 'TRUE',
	'true'		: 'LC_TRUE',
	'False'		: 'FALSE',
	'false'		: 'LC_FALSE',
	'None'		: 'NONE',
	'IMPORT'	: 'IMPORT',
	'CONSTANT'	: 'CONSTANT',
	'NEWEVENT'	: 'NEWEVENT',
	'CELL'		: 'CELL',
	'GADGET'	: 'GADGET',
	'OPTIONS'	: 'OPTIONS',
	'FORALL'	: 'FORALL',
	'IN'		: 'IN',
	'IF'		: 'IF',
	'THEN'		: 'THEN',
	'ELSE'		: 'ELSE',
	'DECLARE'	: 'DECLARE'
}

# The keywords with a colon at the end
ECA = {
	'EVENT:'	: 'EVENT',
	'RULE:'		: 'RULE',
	'CONDITION:'	: 'CONDITION',
	'ACTION:'	: 'ACTION'
}

# All the token names
tokens = [
	'LSBRACK', # [
	'RSBRACK', # ]
	'LCBRACK', # {
	'RCBRACK', # }
	'LPAREN', # (
	'RPAREN', # )
	
	'EQUALS', # = += -=
	'COMPARE', # == <= >= != < >
	
	'PLUS', # +
	'MINUS', # -
	'MODULO', # %
	'TIMDIV', # * /
	
	'COMMA', # ,
	'COLON', # :
	'CNAME', # variable, constant, or event name (does not have to exist yet)
	'NUMBER', # A number (optional dot in it)
	'STRING', # 'text' "text"
	'POINT', # .
	'NEWLINE' # newline(s)
] + list(reserved.values()) + list(ECA.values())

t_ignore	= ' \t'
t_PLUS		= r'\+'
t_MINUS		= r'\-'
t_MODULO	= r'%'
t_TIMDIV 	= r'[\*/]'
t_COLON		= r':'
t_COMMA		= r','
t_POINT		= r'\.'

t_NUMBER	= r'\d+(\.\d+)?'
t_STRING	= r'(\'.*?\')|(".*?")'

t_COMPARE	= r'([<>=!]=)|[<>]'
t_EQUALS	= r'[+-]?='

t_ignore_COMMENT	= r'\#.*|//.*'

# If the parser encountered a LPAREN or LSBRACK the NEWLINE(s) will be ignored untill the same amount or closing brackets are encountered
def t_LPAREN(t):
	r'\('
	t.lexer.paren += 1
	return t
	
def t_RPAREN(t):
	r'\)'
	t.lexer.paren -= 1
	return t
	
def t_LSBRACK(t):
	r'\['
	t.lexer.sbrack += 1
	return t
	
def t_RSBRACK(t):
	r'\]'
	t.lexer.sbrack -= 1
	return t

def t_LCBRACK(t):
	r'\{'
	t.lexer.sbrack += 1
	return t
	
def t_RCBRACK(t):
	r'\}'
	t.lexer.sbrack -= 1
	return t
	
# This token matches all keywords with a colon at the end. Returns the tokens in ECA or an error if it does not match any key in ECA.
def t_EVENT(t):
	r'[A-Z]+:'
	if t.value in ECA:
		t.type = ECA.get(t.value)
	else:
		raise lex.LexError('The keyword "'+t.value+'" is unknown. Line '+str(t.lineno),' ')
	return t
	
# Mathes all variables, constants, or event names (do not have to exist yet). If a match is reserved (in the reserved dict) the token type of this value is returned.
def t_CNAME(t):
	# r'[a-zA-Z][\w\.]*'
	r'[a-zA-Z][\w]*'
	t.type = reserved.get(t.value,'CNAME')
	return t
	
# Is ignored when there are unclosed brackets. Adds the number of newlines to the line number counter.
def t_NEWLINE(t):
	r'\n+'
	t.lexer.lineno += len(t.value)
	if t.lexer.sbrack <= 0 and t.lexer.paren <= 0:
		return t
		
# Is ignored. Adds the number of newlines to the line number counter.
def t_MULTILINECOMMENT(t):
	r'/\*(.|\n)*?((\*/)|$)'
	t.lexer.lineno += len(t.value.split('\n')) - 1
	
lex_error = False

# Raises an error indicating the line number, column and the line the character is in (with a "pointer" to the character making the error).
def t_error(t):
	global lex_error
	lex_error = True
	last_cr = t.lexer.lexdata.rfind('\n',0,t.lexpos)
	if last_cr < 0:
		last_cr = 0
	column = (t.lexpos - last_cr)
	raise lex.LexError('Illegal word or character at line {1} column {2}:\n'.format(t.value[0],t.lineno,column)+t.lexer.lexdata.split('\n')[t.lineno-1]+'\n'+' '*(column-1)+'^',' ')

lexer = lex.lex() # initialize the LEXER
