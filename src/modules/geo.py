import actions
import ECA_parser
import fm

# events = { 'bar' }

def init(arg):
	pass

def deg2dec(deg,min,sec):
	return deg+(((min*60)+(sec))/3600)

def show_user_location(mapid,user,location):
	str = location.lower()
	if "enschede" in str:
		return actions.add_maps_marker(mapid, deg2dec(52,13,6), deg2dec(6,53,45), user)
	elif "almelo" in str:
		return actions.add_maps_marker(mapid, deg2dec(52,21,24), deg2dec(6,39,45), user)
	elif "hengelo" in str:
		return actions.add_maps_marker(mapid, deg2dec(52,15,57), deg2dec(6,47,35), user)
	elif "nijmegen" in str:
		return actions.add_maps_marker(mapid, deg2dec(51,50,33), deg2dec(5,51,10), user)
	elif "amsterdam" in str:
		return actions.add_maps_marker(mapid, deg2dec(52,22,26), deg2dec(4,53,22), user)
	elif "almere" in str:
		return actions.add_maps_marker(mapid, deg2dec(52,22,12), deg2dec(5,12,50), user)
	elif "groningen" in str:
		return actions.add_maps_marker(mapid, deg2dec(53,13,9), deg2dec(6,34,0), user)
	elif "eindhoven" in str:
		return actions.add_maps_marker(mapid, deg2dec(51,26,27), deg2dec(5,28,40), user)
	# print(str)
		
	
builtin_functions = {
	"show_user_location" : ( 3, fm.fcall3(show_user_location))
}

ECA_parser.functions.update( builtin_functions )
