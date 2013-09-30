import ECA_parser
import math
import fm

def init(arg):
	pass

def pi():
	return math.pi

def e():
	return math.e

def minus(arg):
	return - ( arg )

math_functions = {
	"minus" : ( 1, fm.fcall1(minus)),
	"ceil" : ( 1, fm.fcall1(math.ceil)),
	"copysign" : ( 2, fm.fcall2(math.copysign)),
	"fabs" : ( 1, fm.fcall1(math.fabs)),
	"factorial" : ( 1, fm.fcall1(math.factorial)),
	"floor" : ( 1, fm.fcall1(math.floor)),
	"fmod" : ( 1, fm.fcall1(math.fmod)),
	"frexp" : ( 1, fm.fcall1(math.frexp)),
	"fsum" : ( 1, fm.fcall1(math.fsum)),
	"isinf" : ( 1, fm.fcall1(math.isinf)),
	"isnan" : ( 1, fm.fcall1(math.isnan)),
	"ldexp" : ( 2, fm.fcall2(math.ldexp)),
	"modf" : ( 1, fm.fcall1(math.modf)),
	"trunc" : ( 1, fm.fcall1(math.trunc)),
	"exp" : ( 1, fm.fcall1(math.exp)),
	"expm1" : ( 1, fm.fcall1(math.expm1)),
	"log" : ( 2, fm.fcall2(math.log)),
	"log1p" : ( 1, fm.fcall1(math.log1p)),
	"log10" : ( 1, fm.fcall1(math.log10)),
	"pow" : ( 2, fm.fcall2(math.pow)),
	"sqrt" : ( 1, fm.fcall1(math.sqrt)),
	"acos" : ( 1, fm.fcall1(math.acos)),
	"asin" : ( 1, fm.fcall1(math.asin)),
	"atan" : ( 1, fm.fcall1(math.atan)),
	"atan2" : ( 2, fm.fcall2(math.atan2)),
	"cos" : ( 1, fm.fcall1(math.cos)),
	"hypot" : ( 2, fm.fcall1(math.hypot)),
	"sin" : ( 1, fm.fcall1(math.sin)),
	"tan" : ( 1, fm.fcall1(math.tan)),
	"degrees" : ( 1, fm.fcall1(math.degrees)),
	"radians" : ( 1, fm.fcall1(math.radians)),
	"acosh" : ( 1, fm.fcall1(math.acosh)),
	"asinh" : ( 1, fm.fcall1(math.asinh)),
	"atanh" : ( 1, fm.fcall1(math.atanh)),
	"cosh" : ( 1, fm.fcall1(math.cosh)),
	"sinh" : ( 1, fm.fcall1(math.sinh)),
	"tanh" : ( 1, fm.fcall1(math.tanh)),
	"erf" : ( 1, fm.fcall1(math.erf)),
	"erfc" : ( 1, fm.fcall1(math.erfc)),
	"gamma" : ( 1, fm.fcall1(math.gamma)),
	"lgamma" : ( 1, fm.fcall1(math.ceil)),
	"pi" : ( 0, fm.fcall0(pi)),
	"e" : ( 0, fm.fcall0(e))
}

ECA_parser.functions.update( math_functions )
