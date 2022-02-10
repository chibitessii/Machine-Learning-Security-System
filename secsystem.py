import tkinter as tk
from tkinter import *
from tkinter import ttk
from ttkthemes import ThemedTk
import os, haslib, csv
import charseg2

class Application(ttk.Frame):
	def __init__(self, master):
		self.keycode = ""
		self.plate_mfa = 0
		self.keycode_mfa = 0
		ttk.Frame.__init__(self, master)

		def get_plate_pic():
			pic_path = os.path.abspath("col_plate.jpg")
			print(pic_path)
			return pic_path

		def show_whitelist(filename):
			whitelist_file = open(filename, "a+")
			for line in whitelist_file:
				print(line)
			whitelist_file.close()

		def check_whitelist(passcode, filename, mode): 
		    whitelist_file = open(filename, "a+")
		    passcode = hashlib.sha256(passcode.encode()).hexdigest()
		    print(passcode)
		    if mode == "normal":
		        with open(filename) as check_file: 
		            if passcode in check_file.read() and passcode != "": #if this is true check for 2fa, timeout after period of time
		                return True
		            else:
		                return False

		    if mode == "program":
		        with open(filename) as check_file: 
		            if passcode in check_file.read(): #if already in the list, do nothing 
		                return False
		            else:
		                whitelist_file.write("%s\r\n" % (passcode)) #else add to list
		                return True
		    whitelist_file.close()

		def check_mfa(self):
			if self.keycode_mfa !=0 and self.plate_mfa !=0:
				print("mfa passed")
			else:
				print(self.plate_mfa, self.keycode_mfa)
				print("needs another factor")

		def authenticate(self, passcode, filename): #this will work for both keycodes and plate numbers
			if check_whitelist(passcode, filename, "normal") == True:
				print("Authentication Passed")
				if filename == "whitelist.txt":
					self.plate_mfa = 1
				elif filename == "keycode_whitelist.txt":
					self.keycode_mfa = 1
				check_mfa(self)
			else:
				print("Authentication Failed")

		def register(self, passcode, filename): #this will work for both keycodes and plate numbers
			passcode = hashlib.sha256(passcode.encode()).hexdigest()
			if check_whitelist(passcode, filename, "program") == True:
				print("Successfully Registered")
			else:
				print("This Plate Is Already Registered")

		def make_frame(parent, row=0, column=0, sticky=''):
			frame = Frame(parent)
			frame.grid(row=row, column=column, sticky=sticky)
			return frame

		def pressbutton(self, button):
			self.keycode = self.keycode + str(button)
			self.display.insert(END, "*")
			print(self.keycode)

		def clear_keycode(self):
			self.keycode = ""
			self.display.delete('0', 'end')
			self.label.config(text="")

		def make_keypad(self, text):
			if text == 0:
				self.button = ttk.Button(frame5, text= button, command=lambda: pressbutton(self, text), style="AccentButton")
			if text <= 3 and text > 0:
				self.button = ttk.Button(frame2, text= button, command=lambda: pressbutton(self, text), style="AccentButton")
			if text >3 and text <=6:
				self.button = ttk.Button(frame3, text= button, command=lambda: pressbutton(self, text), style="AccentButton")
			if text >6:
				self.button = ttk.Button(frame4, text= button, command=lambda: pressbutton(self, text), style="AccentButton")
			self.button.pack(side=LEFT, fill=None, pady=15, padx=40, expand = False)

		def rescan_plate(self):
			plate_image = get_plate_pic() #interrupt for sensor goes here.
			plate_number = charseg2.CNN_plateRec(plate_image)
			authenticate(self, plate_number, 'whitelist.txt')

		def permission_changed(event):
			return event

		def make_entry(self, frame, width, side):
			self = ttk.Entry(frame, width=width)
			self.pack(side=side)
			return self

		def make_label(self, frame, text):
			self.label = ttk.Label(frame, text=text)
			self.label.pack()
			return self

		def make_button(self, frame, text, command, side, padx=(5,5)):
			self.button = ttk.Button(frame, text=text, command=command, style="AccentButton")
			self.button.pack(side = side, pady = 5, padx = padx)

		def populate_tree(self):
			fieldnames = ['permission', 'name', 'key', 'plate', 'rfid', 'print']
			with open('users.csv', 'r') as file:
				reader = csv.DictReader(file, fieldnames=fieldnames)
				for row in reader:
					permission = row['permission']
					name = row['name']
					key = row['key']
					plate = row['plate']
					rfid = row['rfid']
					fprint = row['print']
					self.user_listbox.insert("", 0, values=(permission, name, key, plate, rfid, fprint))

		def edit_users(self):
			print("makes it here")

		def remove_user(self):
			selection = self.user_listbox.focus()
			member = self.user_listbox.item(selection, 'values')
			member_to_remove = member[1]
			fieldnames = ['permission', 'name', 'key', 'plate', 'rfid', 'print']
			lines = list()
			with open('users.csv', 'r') as file:
				reader = csv.reader(file)
				for row in reader:
					lines.append(row)
					for field in row:
						if field == member_to_remove:
							lines.remove(row)
			with open('users.csv', 'w') as writefile:
				writer = csv.writer(writefile)
				writer.writerows(lines)
			self.user_listbox.delete(self.user_listbox.selection())
			
		def save(self, window):
			fieldnames = ['permission','name', 'key', 'plate', 'rfid','print']
			with open('users.csv', 'a') as  file:
				writer = csv.DictWriter(file, fieldnames=fieldnames)
				writer.writerow({'permission': self.permission_cb.get(),'name': self.name_entry.get(), 'key': self.keycode_entry.get()})
				self.user_listbox.insert("", 0, values=(self.permission_cb.get(), self.name_entry.get(), self.keycode_entry.get()))
			close(self, window)

		def close(self, window):
			window.destroy()
			self.keycode_mfa = 0;
			self.plate_mfa = 0
			self.keycode = ""

		def add_user(self):
			self.user_win = Toplevel()
			#configure_window(self.user_win)
			first_frame = make_frame(self.user_win, sticky = 'n')
			add_frame = make_frame(self.user_win, row=1, sticky = 'n')
			make_button(self, first_frame, "Save", lambda: save(self, self.user_win), LEFT, padx=(0,80))
			make_button(self, first_frame, "Cancel", lambda: close(self, self.user_win), RIGHT, padx=(80,0))
			make_label(self, add_frame, "Permission Level")
			options =["User", "Admin"]
			clicked = StringVar()
			clicked.set("User")
			self.permission_cb = ttk.Combobox(add_frame, textvariable = options)
			self.permission_cb.set("User")
			self.permission_cb['values'] = options
			self.permission_cb['state'] = 'readonly'
			self.permission_cb.pack()
			self.permission_cb.bind('<<ComboboxSelected>>', permission_changed)
			make_label(self, add_frame, "User Name")
			self.name_entry = make_entry(self, add_frame, 12, TOP)
			make_label(self, add_frame, "Key Code")
			self.keycode_entry = make_entry(self, add_frame, 12, TOP)
			make_button(self, add_frame, "Register Plate", register, TOP)
			make_button(self, add_frame, "Register RFID", register, TOP)
			make_button(self, add_frame, "Register Fingerprint", register, TOP)

		def manage_users(self):
			if self.keycode_mfa != 0:
				self.win = Toplevel()
				#configure_window(self.win)
				heading = ['User Type','Username', 'Keycode', 'Plate Number', 'RFID', 'Finger Print']
				user_frame = make_frame(self.win, sticky='nsew')
				user_frame2 = makcone_frame(self.win, row=1, sticky='nsew')
				make_button(self, user_frame, "Add User", command=lambda: add_user(self), side=LEFT)
				make_button(self, user_frame, "Edit User", command=lambda: pressbutton(self, 'test'), side=LEFT)
				make_button(self, user_frame, "Remove User", command=lambda: remove_user(self), side=LEFT)
				make_button(self, user_frame, "Exit", command=lambda: close(self, self.win), side=LEFT)
				self.user_listbox = ttk.Treeview(user_frame2, columns=heading, show='headings')
				[(self.user_listbox.heading(x, text=x), self.user_listbox.column(x, width =120, anchor='center')) for x in heading]
				populate_tree(self)
				self.user_listbox.pack(side=BOTTOM, expand=True, fill = tk.BOTH)
			else:
				self.label.config(text = 'Enter KeyCode')

		def configure_window(window): # makes window fullscreen, ontop of anything else, and expandable 
			#window.attributes('-topmost',True)
			#window.attributes('-fullscreen', True)
			window.columnconfigure(0, weight=1)
			window.rowconfigure(0, weight=1)

		#configure_window(root)
		frame = make_frame(root)
		frame1 = ttk.LabelFrame(root, text='')
		frame1.grid(row=1, column=0, sticky = 'nsew')
		frame2 = make_frame(frame1, row=1, sticky = 'nsew')
		frame3 = make_frame(frame1, row=2, sticky='nsew')
		frame4 = make_frame(frame1, row=3, sticky='nsew')
		frame5 = make_frame(frame1, row=4, sticky='n')
		frame6 = make_frame(root, row=1, column=1, sticky='e')

		self.display = ttk.Entry(frame, font= ('Helvetica 44'))
		self.display.pack(side=TOP, fill=tk.BOTH, pady=15, padx=40, expand=True)
		self.label = ttk.Label(frame1, text = "")
		self.label.grid(row=0,column=0)

		buttons = ['1','2','3','4','5','6','7','8','9','0']
		for button in buttons:
			make_keypad(self, int(button))

		make_button(self, frame6, "Enter", command=lambda: [authenticate(self,self.keycode, "keycode_whitelist.txt"), clear_keycode(self)], side=TOP)
		make_button(self, frame6, "Clear", command=lambda:clear_keycode(self), side=TOP)
		make_button(self, frame6, "Manage Users", command=lambda:manage_users(self), side=TOP)
		make_button(self, frame6, "Rescan Plate", command=lambda:rescan_plate(self), side=TOP)

root=tk.Tk()
root.option_add("*tearOff", False) # This is always a good idea
root.tk.call('source', 'azure-dark.tcl')
ttk.Style().theme_use('azure-dark')
app = Application(root)
root.mainloop()