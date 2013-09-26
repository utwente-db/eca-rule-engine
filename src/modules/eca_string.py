import ECA_parser
import string
import fm

def init(arg):
	pass

def ascii_lowercase():
	return string.ascii_lowercase

def ascii_uppercase():
	return string.ascii_uppercase

def digits():
	return string.digits

def hexdigits():
	return string.hexdigits

def letters():
	return string.letters

def lowercase():
	return string.lowercase

def octdigits():
	return string.octdigits

def punctuation():
	return string.punctuation

def printable():
	return string.printable

def uppercase():
	return string.uppercase

def whitespace():
	return string.whitespace

# m = str.find
# m("foo", "oo")
# 1

string_functions = {
	"ascii_lowercase" : ( 0, fm.fcall0(ascii_lowercase)),
	"ascii_uppercase" : ( 0, fm.fcall0(ascii_uppercase)),
	"digits" : ( 0, fm.fcall0(digits)),
	"hexdigits" : ( 0, fm.fcall0(hexdigits)),
	"letters" : ( 0, fm.fcall0(letters)),
	"lowercase" : ( 0, fm.fcall0(lowercase)),
	"octdigits" : ( 0, fm.fcall0(octdigits)),
	"punctuation" : ( 0, fm.fcall0(punctuation)),
	"printable" : ( 0, fm.fcall0(printable)),
	"uppercase" : ( 0, fm.fcall0(uppercase)),
	"whitespace" : ( 0, fm.fcall0(whitespace)),
	"capitalize" : ( 1, fm.mcall1("capitalize")),
	"find"   : ( 2, fm.mcall2("find")), # INCOMPLETE, more poss
	"rfind" : ( 2, fm.mcall2("rfind")), # INCOMPLETE, more poss
	"index" : ( 2, fm.mcall2("index")), # INCOMPLETE, more poss
	"rindex" : ( 2, fm.mcall2("rindex")), # INCOMPLETE, more poss
	"count" : ( 2, fm.mcall2("count")), # INCOMPLETE, more poss
	"lower" : ( 1, fm.mcall1("lower")),
	"split" : ( 2, fm.mcall2("split")), # INCOMPLETE, more poss
	"rsplit" : ( 2, fm.mcall2("rsplit")), # INCOMPLETE, more poss
	"join" : ( 2, fm.mcall2("join")), # INCOMPLETE, more poss
	"lstrip" : ( 2, fm.mcall2("lstrip")), # INCOMPLETE, more poss
	"rstrip" : ( 2, fm.mcall2("rstrip")), # INCOMPLETE, more poss
	"strip" : ( 2, fm.mcall2("strip")), # INCOMPLETE, more poss
	"swapcase" : ( 1, fm.mcall1("swapcase")),
	"translate" : ( 3, fm.mcall3("translate")),
	"upper" : ( 1, fm.mcall1("upper")),
	"ljust" : ( 3, fm.mcall3("ljust")),
	"rjust" : ( 3, fm.mcall3("rjust")),
	"center" : ( 3, fm.mcall3("center")),
	"zfill" : ( 2, fm.mcall2("zfill")),
	"replace" : ( 3, fm.mcall3("replace"))
	# slice/substring is defined in standaard.py
}

ECA_parser.functions.update( string_functions )
