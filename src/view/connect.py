import tkinter as tk

def init(frame,host,user,password,database):
	frame.master.title("Connect to a database")
	frame.master.resizable(0,0)
	panel = tk.Frame()
	panel.place(in_=frame, anchor="c", relx=.5, rely=.5)
	
	# connect button
	frame.button_connect = tk.Button(panel,text="Connect",command=frame.connect_database)
	frame.button_connect.grid(row=4,column=0,columnspan=2,pady=5)

	frame.change_button(frame.check_fields())
	frame.pack(expand=True)
	
	# host name
	tk.Label( panel, text="The host adress: ").grid(row=0,column=0)
	frame.host_field = tk.StringVar()
	temp = tk.Entry(panel,textvariable=frame.host_field,validate="key",validatecommand=(frame.master.register(lambda value:frame.key_press(value,0)),'%P'))
	temp.grid(row=0,column=1)
	temp.bind("<Return>",frame.connect_database)
	frame.host_field.set(host)
	
	# user name
	tk.Label( panel, text="Your username: ").grid(row=1,column=0)
	frame.user_field = tk.StringVar()
	temp = tk.Entry(panel,textvariable=frame.user_field,validate="key",validatecommand=(frame.master.register(lambda value:frame.key_press(value,1)),'%P'))
	temp.grid(row=1,column=1)
	temp.bind("<Return>",frame.connect_database)
	frame.user_field.set(user)
	
	# # password
	tk.Label( panel, text="Your password: ").grid(row=2,column=0)
	frame.pass_field = tk.StringVar()
	temp = tk.Entry(panel,textvariable=frame.pass_field,show="*",validate="key",validatecommand=(frame.master.register(lambda value:frame.key_press(value,2)),'%P'))
	temp.grid(row=2,column=1)
	temp.bind("<Return>",frame.connect_database)
	frame.pass_field.set(password)
	
	# database name
	tk.Label( panel, text="The database: ").grid(row=3,column=0)
	frame.db_field = tk.StringVar()
	temp = tk.Entry(panel,textvariable=frame.db_field,validate="key",validatecommand=(frame.master.register(lambda value:frame.key_press(value,3)),'%P'))
	temp.grid(row=3,column=1)
	temp.bind("<Return>",frame.connect_database)
	frame.db_field.set(database)
	
if __name__ == '__main__':
	host = 'host'
	user = ''
	password = ''
	database = ''
	
	class connect_frame(tk.Frame):
		### View
		def __init__(self,master=None):
			global host,user,password,database
			tk.Frame.__init__(self, master=None,width=350, height=170)
			init(self,host,user,password,database)
			
		### control
		def connect_database(self,*arg):
			print('connect')
		def check_fields(self):
			print('check')
		def change_button(self,enable):
			print('enable')
		def key_press(self,*event):
			print('key press')
			return True
			
	root = tk.Tk()
	connect = connect_frame()
	connect.mainloop()