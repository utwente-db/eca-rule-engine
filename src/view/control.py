import tkinter as tk

class Gauge:
	def __init__(self,master,width,height):
		self.width = width
		self.height = height
		self.canvas = tk.Canvas(master,width=width,height=height,bg='gray',borderwidth=2,relief=tk.SOLID)
		self.value = 0
		self.error = False
		self.done = True
		self.rectangle = self.canvas.create_rectangle(0,0,0,0)
		self.text = self.canvas.create_rectangle(0,0,0,0)
		self.draw()
		
	def draw(self):
		try:
			self.canvas.delete(self.rectangle)
			self.canvas.delete(self.text)
			self.rectangle = self.canvas.create_rectangle(3, 3, int(self.width/100*self.value)+3, self.height+5, fill=self.color())
			self.text = self.canvas.create_text(int(self.width/2+3),int(self.height/2+3),text=str(self.value)+'%',fill='white')
		except:
			pass
		
	def set(self,value,done=False,error=False):
		self.done = done
		self.error = error
		self.value = value
		self.draw()
		
	def color(self):
		if self.error:
			return 'red'
		elif self.done:
			return 'green'
		else:
			return 'blue'
			
def init(frame):
	frame.master.title('Connect to a database')
	frame.master.minsize(500,400)
	
	## Menu
	menu = tk.Menu(frame.master)
	frame.master.config(menu=menu)
	
	## Database menu
	# database_menu = tk.Menu(menu,tearoff=0)
	# menu.add_cascade(label="Database",menu=database_menu)
	
	# database_menu.add_command(label="Disconnect", command=frame.disconnect)
	# frame.Bind(wx.EVT_MENU,frame.disconnect,database_menu.Append(wx.ID_ANY,"&Disconnect"," Disconnect from the SQL server"))
	
	## ECA menu
	frame.ECA_menu = tk.Menu(menu,tearoff=0)
	menu.add_cascade(label="ECA file",menu=frame.ECA_menu)
	
	frame.ECA_menu.add_command(label="Load ECA file...",command=frame.load_ECA_file_event)
	frame.ECA_menu.add_command(label="Reload ECA file",command=frame.reload_ECA_file)
	frame.ECA_menu.add_command(label="Discard ECA file",command=frame.discard_ECA_file)
	frame.ECA_menu.add_separator()
	frame.auto_reload = tk.BooleanVar()
	frame.ECA_menu.add_checkbutton(label="Auto reload files",variable=frame.auto_reload)
	frame.auto_reload.set(True)
	# ECA_menu.Append(wx.ID_OPEN,," Load an ECA file in the rule engine")
	# ECA_menu.Append(wx.ID_REDO,"&Reload ECA file\tF5"," Reload the ECA file")
	# ECA_menu.Append(wx.ID_CLOSE,"&Discard ECA file\tCtrl+D"," Discard the ECA file")
	
	## Rule Engine menu
	frame.RE_menu = tk.Menu(menu,tearoff=0)
	menu.add_cascade(label="Rule engine",menu=frame.RE_menu)
	
	frame.RE_menu.add_command(label="Start the rule engine",command=frame.start_rule_engine)
	frame.RE_menu.add_command(label="Stop the rule engine",command=frame.stop_rule_engine)
	frame.RE_menu.add_separator()
	# frame.RE_menu.add_command(label="Show the output",command=frame.show_output)
	# RE_menu.Append(wx.ID_ANY,"&"," Start the rule engine")
	# RE_menu.Append(wx.ID_ANY,"&"," Stop the rule engine")
	# RE_menu.Append(wx.ID_ANY,"&"," Show the output of the rule engine")
	
	menu.add_command(label="Exit",command=frame.master.destroy)
	
	## Controls
	controls = tk.Frame()
	controls.pack()
	
	## ECA file control buttons
	ECA_box = tk.LabelFrame(controls, text="ECA file controls", padx=5, pady=5)
	ECA_box.grid(row=0,column=0,padx=5,pady=5)
	
	frame.load_button = tk.Button(ECA_box, text="Load ECA file...",command=frame.load_ECA_file_event)
	frame.load_button.grid(row=0,column=0)
	
	frame.reload_button = tk.Button(ECA_box, text="Reload ECA file",command=frame.reload_ECA_file)
	frame.reload_button.grid(row=1,column=0)
	
	frame.discard_button = tk.Button(ECA_box, text="Discard ECA file",command=frame.discard_ECA_file)
	frame.discard_button.grid(row=2,column=0)
	
	## start time & date picker
	start_time_box = tk.LabelFrame(controls, text='Starting time', padx=5, pady=5)
	start_time_box.grid(row=0,column=1,padx=5,pady=5)
	
	frame.set_start_button = tk.Button(start_time_box,text='Set to first tweet',command=frame.set_first_time)
	frame.set_start_button.grid(row=0,column=0,columnspan=4)
	
	tk.Label(start_time_box,text='Time: ').grid(row=1,column=0,pady=5)
	
	frame.start_time_ctrl = []
	frame.start_time_ctrl.append(tk.Spinbox(start_time_box,width=2,values=list(range(24))))
	frame.start_time_ctrl.append(tk.Spinbox(start_time_box,width=2,values=list(range(60))))
	frame.start_time_ctrl.append(tk.Spinbox(start_time_box,width=2,values=list(range(60))))
	
	tk.Label(start_time_box,text='Date: ').grid(row=2,column=0)
	
	frame.start_time_ctrl.append(tk.Spinbox(start_time_box,width=2,values=list(range(1,32))))
	frame.start_time_ctrl.append(tk.Spinbox(start_time_box,width=2,values=list(range(1,13))))
	
	for x in range(3):
		frame.start_time_ctrl[x].grid(row=1,column=x+1)
	for x in range(3,5):
		frame.start_time_ctrl[x].grid(row=2,column=x-2)
	
	## stop time & date picker
	stop_time_box = tk.LabelFrame(controls, text='Stopping time', padx=5, pady=5)
	stop_time_box.grid(row=0,column=2,padx=5,pady=5)
	
	frame.set_start_button = tk.Button(stop_time_box,text='Set to last tweet',command=frame.set_last_time)
	frame.set_start_button.grid(row=0,column=0,columnspan=4)
	
	tk.Label(stop_time_box,text='Time: ').grid(row=1,column=0,pady=5)
	
	frame.stop_time_ctrl = []
	frame.stop_time_ctrl.append(tk.Spinbox(stop_time_box,width=2,values=list(range(24))))
	frame.stop_time_ctrl.append(tk.Spinbox(stop_time_box,width=2,values=list(range(60))))
	frame.stop_time_ctrl.append(tk.Spinbox(stop_time_box,width=2,values=list(range(60))))
	
	tk.Label(stop_time_box,text='Date: ').grid(row=2,column=0)
	
	frame.stop_time_ctrl.append(tk.Spinbox(stop_time_box,width=2,values=list(range(1,32))))
	frame.stop_time_ctrl.append(tk.Spinbox(stop_time_box,width=2,values=list(range(2,6))))
	
	for x in range(3):
		frame.stop_time_ctrl[x].grid(row=1,column=x+1)
	for x in range(3,5):
		frame.stop_time_ctrl[x].grid(row=2,column=x-2)
	
	## speed picker
	speed_box = tk.LabelFrame(controls, text='Simulation speed', padx=5, pady=5)
	speed_box.grid(row=1,column=0,padx=5,pady=5)
	
	frame.speed_label = tk.StringVar()
	frame.speed_label.set('10^5')
	
	frame.speed_ctrl = tk.Scale(speed_box, from_=10,to=0,command=lambda *arg: frame.speed_label.set('10^%s'%arg[0]))
	frame.speed_ctrl.set(5)
	frame.speed_ctrl.grid(row=0,column=0)
	
	tk.Label(speed_box,textvariable=frame.speed_label).grid(row=0,column=1)
	
	## Rule engine control buttons
	RE_box = tk.LabelFrame(controls, text='Rule Engine controls', padx=5, pady=5)
	RE_box.grid(row=1,column=1,columnspan=2,padx=5,pady=5)
	
	## gauge
	frame.gauge = Gauge(RE_box,200,20)
	frame.gauge.canvas.grid(row=0,column=0,columnspan=2)
	
	## start & stop
	frame.start_button = tk.Button(RE_box,text="Start the rule engine",command=frame.start_rule_engine)
	frame.start_button.grid(row=1,column=0)
	frame.stop_button = tk.Button(RE_box,text="Stop the rule engine",command=frame.stop_rule_engine)
	frame.stop_button.grid(row=1,column=1)
	# frame.output_button = tk.Button(RE_box,text="Show the output",command=frame.show_output)
	# frame.output_button.grid(row=2,column=0,columnspan=2)
	
	## Status updates field
	frame.status = tk.Text(frame,wrap=tk.WORD,font='courier 12')
	frame.status.insert(tk.END,'No file is loaded. Building cache...')
	frame.status.config(state=tk.DISABLED)
	frame.status.tag_config("split", foreground="gray")
	frame.status.tag_config("error", foreground="red")
	frame.status.pack(side=tk.BOTTOM,fill=tk.BOTH, expand=1)
	
	frame.master.bind("<FocusIn>",frame.on_focus)
	frame.pack(fill=tk.BOTH, expand=1)
	
if __name__ =='__main__':
	class controls_frame(tk.Frame):
		### View
		def __init__(self):
			tk.Frame.__init__(self, master=None)
			init(self)
			
		### Control
		def disconnect(self,event=None):
			print("disconnect")
		def start_rule_engine(self,event=None):
			pass
		def stop_rule_engine(self,event=None):
			pass
		def on_result(self,event=None):
			pass
		def load_ECA_file(self,file_path):
			pass
		def load_ECA_file_event(self,event=None):
			pass
		def reload_ECA_file(self,event=None):
			pass
		def discard_ECA_file(self,event=None):
			pass
		def display_loaded(self):
			pass
		def show_output(self,event=None):
			pass
		def on_focus(self,event=None):
			print('focus')
		def show_text(self,message,error=False):
			pass
		def set_first_time(self,event=None):
			self.gauge.set((self.gauge.value+5)%105)
			print(('f',self.gauge.value))
		def set_last_time(self,event=None):
			print('l')
			
	temp = controls_frame()
	import threading
	import time
	
	def f(self):
		x = 0
		while True:
			self.gauge.set((self.gauge.value+1)%105,x<5,x>15)
			time.sleep(0.1)
			x = (x+1) % 20
	t = threading.Thread(target=f,args=[temp])
	t.daemon = True #if parent dies, kill thread
	t.start()
	temp.mainloop()
