import os, re, time, threading, queue
from datetime import datetime

import tkinter as tk
from tkinter.messagebox import showwarning, showerror
from tkinter.filedialog import askopenfilename

## import OUI
import view.connect
import view.control

## modules for Model
# import dbconnect
import dboffline as dbconnect
import rengine

import traceback

import tweetprocessor

dirname = os.getcwd()

class Observer(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self,daemon=True)
		self.controls = None
		self.q = queue.Queue()
		
	def info(self,data):
		self.q.put(data)
		
	def run(self):
		while True:
			data = self.q.get()
			if data is None:
				break
			try:
				while not self.controls:
					self.controls.wait()
				self.controls.new_result(data)
			except Exception as e:
				print(e)
				break
		while not self.q.empty():
			self.q.get()
		# print('Observer stopped')

# create a new Observer
observer = Observer()
observer.name = "DUI_global_observer"

def state(enable):
	if enable:
		return tk.NORMAL
	else:
		return tk.DISABLED
		
## Class for the 'connect' frame
class connect_frame(tk.Frame):
	### View
	def __init__(self):
		global host,user,password,database
		tk.Frame.__init__(self, master=None,width=350, height=170)
		self.valid = [False,False,False,False]
		view.connect.init(self,host,user,password,database)
		
	### control
	def connect_database(self,*event):
		global host,user,password,database,connected
		self.change_button(False)
		if self.check_fields():
			if dbconnect.connect_to_db(str(self.host_field.get()),str(self.user_field.get()),str(self.pass_field.get()),str(self.db_field.get()),input_observer=observer):
				host = str(self.host_field.get())
				user = str(self.user_field.get())
				password = str(self.pass_field.get())
				database = str(self.db_field.get())
				# save_settings()
				connected = True
				self.master.destroy()
			else:
				showwarning('Unable to connect','Incorrect credentials or database.')
				self.change_button(self.check_fields())
		else:
			showwarning('Incorrect input','Incorrect input, please check the fields.')
			self.change_button(self.check_fields())
		
	def check_fields(self):
		for x in self.valid:
			if not x:
				return False
		return True
		
	def change_button(self,enable):
		if enable:
			self.button_connect.config(state=tk.NORMAL)
		else:
			self.button_connect.config(state=tk.DISABLED)
		
	def key_press(self,value,field):
		if field == 0:
			self.valid[field] = len(value) > 0
		else:
			regex = re.compile(r'[a-zA-Z][A-Za-z0-9_]*$')
			self.valid[field] = regex.match(value) is not None
		self.change_button(self.check_fields())
		return True
		
## Window with the controls of the rule engine ########################
class controls_frame(tk.Frame):
	### View
	def __init__(self, master=None):
		tk.Frame.__init__(self, master)
		self.file_loaded = False
		self.file_path = None
		self.file_time = None
		self.working = False
		observer.controls=self
		observer.start()
		dbconnect.observer = observer
		view.control.init(self)
		self.display_loaded()
		
	### Control
	def disconnect(self):
		global reconnect
		reconnect = True
		dbconnect.disconnect()
		self.destroy()
		
	def start_rule_engine(self):
		try:
			result = rengine.start_rule_engine(start_time=self.get_start_time(),stop_time=self.get_stop_time(),speed=self.get_speed(),observer=observer,produce=tpt.get_produce_function(),threadsync_event=tweetprocessor.EVENT)
			if result:
				self.show_text('Rule engine not started\n'+str(result),True)
				self.working = False
				self.gauge.set(0)
			else:
				self.working = True
				self.show_text('Rule engine working')
				self.gauge.set(1)
			self.display_loaded()
		except:
			self.show_text('Rule engine not started\n'+str(result),True)
			self.working = False
			self.gauge.set(0)
			
	def stop_rule_engine(self):
		rengine.stop_rule_engine()
		
	def new_result(self,data):
		if isinstance(data,tuple):
			if data[0] is not None:
				self.working = data[0]
			if data[1] is not None:
				self.gauge.set(data[1])
			if data[2] is not None and data[3] is not None:
				self.show_text(data[2],data[3])
			self.display_loaded()
		else:
			disconnect(None)
			showerror('Rule engine shutdown',str(data))
		
	def load_ECA_file(self,file_path):
		result = rengine.load_file(file_path)
		self.file_path = file_path
		self.file_time = os.stat(self.file_path).st_mtime
		if not result:
			self.file_loaded = True
			self.show_text('File loaded succesfully.')
		else:
			self.file_loaded = False
			self.show_text('The file was not loaded!\n\n'+str(result),True)
		self.display_loaded()
		

	def load_ECA_file_event(self):
		global dirname
		result = askopenfilename(filetypes=(('ECA file','*.ECA'),),initialdir=dirname,parent=self,title='Open an ECA file')
		if result:
			dirname = os.path.dirname(result)
			# save_settings()
			self.load_ECA_file(result)
			self.set_first_time()
			self.set_last_time()
			
	def reload_ECA_file(self):
		## INCOMPLETE check
		self.load_ECA_file(self.file_path)
		
	def discard_ECA_file(self):
		rengine.discard_file()
		self.file_loaded = False
		self.file_path = None
		self.display_loaded()
		self.show_text('File discarded.')
		
	def display_loaded(self):
		loaded = self.file_path is not None
		
		self.ECA_menu.entryconfigure(0,state=state(not self.working))
		self.load_button.config(state=state(not self.working))
		
		self.ECA_menu.entryconfigure(1,state=state(loaded and not self.working))
		self.reload_button.config(state=state(loaded and not self.working))
		
		self.ECA_menu.entryconfigure(2,state=state(loaded and not self.working))
		self.discard_button.config(state=state(loaded and not self.working))
		
		self.RE_menu.entryconfigure(0,state=state(self.file_loaded and not self.working))
		self.start_button.config(state=state(self.file_loaded and not self.working))
		
		self.RE_menu.entryconfigure(1,state=state(self.file_loaded and self.working))
		self.stop_button.config(state=state(self.file_loaded and self.working))
		
	## TODO
	def show_output(self):
		pass
		
	def on_focus(self,event):
		if self.auto_reload.get() and self.file_path is not None and not self.working and self.file_time != os.stat(self.file_path).st_mtime:
			self.load_ECA_file(self.file_path)
			
	def show_text(self,message,error=False):
		self.status.config(state=tk.NORMAL)
		mlen = len(message.split('\n'))
		while len(self.status.get('0.0',tk.END).split('\n')) - 13 + mlen > 0:
			self.status.delete('0.0','0.0 + 1 lines')
		self.status.insert(tk.END,'\n----\n',("split",))
		if error:
			self.status.insert(tk.END,str(message),('error',))
		else:
			self.status.insert(tk.END,str(message))
		self.status.config(state=tk.DISABLED)
		
	def set_first_time(self):
		if dbconnect.cache_done:
			temp = time.gmtime(dbconnect.times[0])
			self.start_time_ctrl[0].delete(0,tk.END)
			self.start_time_ctrl[0].insert(0,temp.tm_hour)
			
			self.start_time_ctrl[1].delete(0,tk.END)
			self.start_time_ctrl[1].insert(0,temp.tm_min)
			
			self.start_time_ctrl[2].delete(0,tk.END)
			self.start_time_ctrl[2].insert(0,temp.tm_sec)
			
			self.start_time_ctrl[3].delete(0,tk.END)
			self.start_time_ctrl[3].insert(0,temp.tm_mday)
			
			self.start_time_ctrl[4].delete(0,tk.END)
			self.start_time_ctrl[4].insert(0,temp.tm_mon)
		else:
			self.show_text('The cache is not yet made, please try again later.',True)
		
	def set_last_time(self):
		if dbconnect.cache_done:
			temp = time.gmtime(dbconnect.times[-1])
			self.stop_time_ctrl[0].delete(0,tk.END)
			self.stop_time_ctrl[0].insert(0,temp.tm_hour)
			
			self.stop_time_ctrl[1].delete(0,tk.END)
			self.stop_time_ctrl[1].insert(0,temp.tm_min)
			
			self.stop_time_ctrl[2].delete(0,tk.END)
			self.stop_time_ctrl[2].insert(0,temp.tm_sec)
			
			self.stop_time_ctrl[3].delete(0,tk.END)
			self.stop_time_ctrl[3].insert(0,temp.tm_mday)
			
			self.stop_time_ctrl[4].delete(0,tk.END)
			self.stop_time_ctrl[4].insert(0,temp.tm_mon)
		else:
			self.show_text('The cache is not yet made, please try again later.',True)
		
	def get_start_time(self):
		try:
			start_time = datetime(
				year=2013,
				month=int(self.start_time_ctrl[4].get()),
				day=int(self.start_time_ctrl[3].get()),
				hour=int(self.start_time_ctrl[0].get()),
				minute=int(self.start_time_ctrl[1].get()),
				second=int(self.start_time_ctrl[2].get())
			)
			return time.mktime(time.struct_time(start_time.timetuple()))
		except:
			showwarning('Incorrect start time','The starting time you entered is incorrect')
			raise Exception()
		
	def get_stop_time(self):
		try:
			stop_time = datetime(
				year=2013,
				month=int(self.stop_time_ctrl[4].get()),
				day=int(self.stop_time_ctrl[3].get()),
				hour=int(self.stop_time_ctrl[0].get()),
				minute=int(self.stop_time_ctrl[1].get()),
				second=int(self.stop_time_ctrl[2].get())
			)
			return time.mktime(time.struct_time(stop_time.timetuple()))
		except:
			showwarning('Incorrect stop time','The stopping time you entered is incorrect')
			raise Exception()
		
	def get_speed(self):
		return 10 ** self.speed_ctrl.get()
		
def save_settings():
	global host,user,password,database,dirname
	settings = open("settings.ini",'w')
	settings.write(str(host)+'\n')
	settings.write(str(user)+'\n')
	settings.write(str(password)+'\n')
	settings.write(str(database)+'\n')
	settings.write(str(dirname)+'\n')
	settings.close()
	
def show_connect():
	global connected,host,user,password,database,dirname
	connected = False
	try:
		settings = open("settings.ini",'r')
		lines = settings.read().split('\n',5)
		settings.close()
		host = lines[0]
		user = lines[1]
		password = lines[2]
		database = lines[3]
		dirname = lines[4]
		connect_frame().mainloop()
	except Exception as e:
		host = ''
		user = ''
		password = ''
		database = ''
		dirname = os.path.expanduser('~')
		# save_settings()
		connect_frame().mainloop()
	return connected
	
def show_controls(master):
	global reconnect
	reconnect = False
	controls_frame(master).mainloop()
	if observer.is_alive():
		observer.info(None)
	observer.controls = None
	return reconnect
	
class tweetprocessorThread (threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		tweetprocessor.process_tweets(7737)
	def get_produce_function(self):
		return tweetprocessor.get_produce_function()

tpt = None

def cleanup(reason):
    # stop_threads() signals the rule engine and HTTP server thread(s) to stop:
    stop_threads(reason)
    # after being signalled by stop_threads() above, it is very well possible
    # that there are still threads running. It is even possible that a new one
    # has been created because of a quick retry by a connected browser. So we
    # keep on trying. As this code may be called from a KeyboardInterrupt
    # handler, we have to handle our own KeyboardInterrupts.
    while threading.active_count() > 1:
        for _t in threading.enumerate():
            try:
                if _t.name == "rule_engine_thread":
                    rengine.stop_rule_engine()
                    tweetprocessor.EVENT.set()
                if _t != threading.current_thread():
                    _t.join(0.1)
            except KeyboardInterrupt:
                stop_threads(reason)


def stop_threads(reason):
    # rengine.stop_rule_engine() is robust, so we simply call it, won't
    # harm if the rule engine has already stopped or the thread doesn't
    # exist anymore:
    rengine.stop_rule_engine()
    # There are scenarios where the rule engine can't stop because it is
    # still waiting on EVENT to be set, so we set it. It is robust, so no
    # problem if the rule engine has already stopped:
    tweetprocessor.EVENT.set()
    # Stop the HTTP server in a clean way:
    tweetprocessor.shutdown_tweetprocessor(reason)
    # Stop the Obserer instance created as global in DUI.py:
    observer.info(None)
    

if __name__ == '__main__':
	## INCOMPLETE check if a running tweetprocessor has to be killed
	try:
		tpt = tweetprocessorThread()
		tpt.name = "tpt_thread"
		tpt.start()
		root = tk.Tk()
		while True:
			# if not show_connect():
				# break
			if not show_controls(master=root):
				break
		dbconnect.disconnect()
		cleanup("Main graphical user interface window closed")
	except KeyboardInterrupt:
		# This exception is raised upon receiving CTRL-C or SIGINT
		cleanup("CTRL-C or SIGINT received")
		root.destroy()


