import csv
import ECA_parser
import fm

# events = { 'bar' }

def init(arg):
	pass

def csv_read_kv_dict(csvname,kidx,vidx):
    with open(csvname,mode='r') as infile:
       reader = csv.reader(infile)
       retdict = {}
       for rows in reader:
            k = rows[kidx]
            v = rows[vidx]
            retdict[k] = v
       return retdict

standard_functions = {
	"csv_read_kv_dict" : ( 3, fm.fcall3(csv_read_kv_dict)),
	#
	"slice" : ( 3, (lambda input: lambda event: (tuple(input[1](event))[0])[(input[1](event)[1]):(input[1](event)[2])])),
	"hslice" : ( 2, (lambda input: lambda event: (tuple(input[1](event))[0])[:(input[1](event)[1])])),
	"tslice" : ( 2, (lambda input: lambda event: (tuple(input[1](event))[0])[(input[1](event)[1]):])),
	"substring" : ( 3, (lambda input: lambda event: (tuple(input[1](event))[0])[(input[1](event)[1]):(input[1](event)[2])])),
	#
	"len" : ( 1, fm.fcall1(len))
}



ECA_parser.functions.update( standard_functions )
