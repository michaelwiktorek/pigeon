"""
Pigeon is a peer-to-peer chat client with end-to-end encryption.
Copyright (C) 2016 Michael Wiktorek
"""

import Tkinter as tk
import tkMessageBox as messagebox
from Queue import Queue
import sys

class Tkinter_Gui:

    def __init__(self):
        self.HANDLES_MAIN_LOOP = True

        try:
            self.parent = tk.Tk()
        except:
            print "Tkinter GUI will not work without a display!"
            sys.exit(0)
        self.parent.wm_title("pigeon")

        self.user_text = Queue()
        self.controller = None
    
        self.container1 = tk.Frame(self.parent)
        self.container1.pack()

        self.system_box = tk.Text(self.container1, state="disabled")
        self.system_box.configure(height=15, borderwidth=3, highlightbackground="black")
        self.system_box.pack(side=tk.TOP)

        self.chat_box = tk.Text(self.container1, state="disabled")
        self.chat_box.configure(borderwidth=3, highlightbackground="black")
        self.chat_box.pack(side=tk.TOP)

        self.userlist_box = tk.Text(self.container1, state="disabled")
        self.userlist_box.configure(height=4, borderwidth=3, highlightbackground="black")
        self.userlist_box.pack(side=tk.TOP)

        self.textbox = tk.Entry(self.container1, width=70)
        self.textbox.pack(side=tk.TOP)
        #self.textbox.bind("<Return>", self.write_junk)
        self.textbox.bind("<Return>", self.handle_text)
        self.textbox.focus_force()

        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.controller.handle_text("/quit")

    # Begin pigeon gui interface implementation ~~~
        
    def sys_write(self, message):
        self.system_box.configure(state="normal")
        self.system_box.insert("end", "SYSTEM: " + message + "\n")
        self.system_box.see(tk.END)
        self.system_box.configure(state="disabled")
        self.parent.update()

    def chat_write(self, message, name):
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", name + ": " + message + "\n")
        self.chat_box.see(tk.END)
        self.chat_box.configure(state="disabled")
        self.parent.update()

    def chat_notify(self, message):
        self.chat_write(message, "SYSTEM")

    # this will need some work if gui handles the main loop
    def get_text(self):
        return

    def start_gui(self, controller):
        self.controller = controller
        self.parent.after(0, self.controller.start_writing)
        self.main_loop()
        return

    def end_gui(self):
        self.parent.destroy()

    def print_userlist(self, userlist):
        self.userlist_box.delete(0, tk.END)
        self.userlist_box.configure(state="normal")
        for addr in userlist.keys():
            self.userlist_box.insert("end", userlist[addr][0] + " at " + addr + "\n")
        self.userlist_box.configure(state="disabled")

    # End pigeon gui interace implementation ~~~

    # we call this on <Return> from the textbox
    # it behaves like the controller's main_loop
    def handle_text(self, event):
        if self.controller.ALIVE:
            text = self.textbox.get()
            self.textbox.delete(0, tk.END)
            if self.controller.HANGUP:
                self.controller.handle_hangup()
                return
            self.controller.handle_text(text)

    

    def main_loop(self):
        self.parent.mainloop()

if __name__ == "__main__":
    my_gui = Tkinter_Gui()
    my_gui.main_loop(None)
