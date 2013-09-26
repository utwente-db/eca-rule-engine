# function macro module

#
# The macros for function calls
# 

def fcall0(f):
	return lambda input: lambda event: f() 

def fcall1(f):
	return lambda input: lambda event: f(str(*tuple(input[1](event)))) 

def fcall2(f):
	return lambda input: lambda event: f(tuple(input[1](event))[0],tuple(input[1](event))[1])

def fcall3(f):
	return lambda input: lambda event: f(tuple(input[1](event))[0],tuple(input[1](event))[1],tuple(input[1](event))[2])

def fcall4(f):
	return lambda input: lambda event: f(tuple(input[1](event))[0],tuple(input[1](event))[1],tuple(input[1](event))[2],tuple(input[1](event))[3])

#
# The macros for method calls, could be more efficient
# 

def mcall1(mn):
	return lambda input: lambda event: (tuple(input[1](event))[0]).__getattribute__(mn)()

def mcall2(mn):
	return lambda input: lambda event: (tuple(input[1](event))[0]).__getattribute__(mn)(input[1](event)[1])

def mcall3(mn):
	return lambda input: lambda event: (tuple(input[1](event))[0]).__getattribute__(mn)(input[1](event)[1],input[1](event)[2])

