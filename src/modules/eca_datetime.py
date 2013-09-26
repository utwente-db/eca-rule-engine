import ECA_parser
from datetime import tzinfo, timedelta, date, datetime
import fm

def init(arg):
	pass

# incomplete, which functions do we need here 

datetime_functions = {
	"date" : ( 3, fm.fcall3(datetime.date)),
	"datetime" : ( 6, fm.fcall6(datetime.date)),
	"today" : ( 1, fm.fcall1(datetime.today))
}

ECA_parser.functions.update( datetime_functions )
