"""
Pigeon is a peer-to-peer chat client with end-to-end encryption.
Copyright (C) 2016 Michael Wiktorek
"""

import sys
import Tkinter      as tk
import tkMessageBox as messagebox
from Queue            import Queue
from pigeon_constants import Pigeon_Constants as C

class Tkinter_Gui:

    def __init__(self):
        self.CMD_MSG = {"/connect" : "Enter an IP address or name to connect to!",
               "/rename"  : "Enter a new name for yourself!",
               "/register": "Enter the IP address of a registration server!"}
        self.init_window_stuff()
        self.init_buttons()
        self.init_text_widgets()
        self.set_handlers()
        
    def init_window_stuff(self):
        # HANDLES_MAIN_LOOP described in gui_spec.txt
        self.HANDLES_MAIN_LOOP = True
        try:
            self.parent = tk.Tk()
        except:
            print "Tkinter GUI will not work without a display!"
            sys.exit(0)
        self.parent.wm_title("pigeon")
        self.user_text = Queue()
        self.controller = None

    def init_buttons(self):
        self.button_frame = tk.Frame(self.parent)
        self.button_frame.pack(side=tk.LEFT)

        self.buttons = []
        for cmd in C.CMD_LIST:
            label = cmd.lstrip('/').title()
            if cmd in C.CMD_LIST_ARGS:
                message = self.CMD_MSG[cmd]
                self.buttons.append(tk.Button(self.button_frame, text=label, width=12,
                                              command=lambda arg1=cmd, arg2=message : self.command_arg(arg1, arg2)))
            else:
                self.buttons.append(tk.Button(self.button_frame, text=label, width=12,
                                              command=lambda arg1=cmd : self.command(arg1)))
                                    
        for button in self.buttons:
            button.pack(side=tk.TOP)
        

    def init_text_widgets(self):
        # frame to hold text widgets
        self.text_frame = tk.Frame(self.parent)
        # system box prints system messages
        self.system_box = tk.Text(self.text_frame, state="disabled")
        self.system_box.configure(height=15, borderwidth=3, highlightbackground="black")
        # chat box prints chat messages
        self.chat_box = tk.Text(self.text_frame, state="disabled")
        self.chat_box.configure(borderwidth=3, highlightbackground="black")
        # userlist box contains userlist from reg. server
        self.userlist_box = tk.Text(self.text_frame, state="disabled")
        self.userlist_box.configure(height=4, borderwidth=3, highlightbackground="black")
        # user types commands/messages in text box
        self.textbox = tk.Entry(self.text_frame, width=70)
        self.textbox.focus_force()
        # pack widgets
        self.text_frame.pack(side=tk.LEFT)
        self.system_box.pack(side=tk.TOP)
        self.chat_box.pack(side=tk.TOP)
        self.userlist_box.pack(side=tk.TOP)
        self.textbox.pack(side=tk.TOP)  

    def set_handlers(self):
        self.textbox.bind("<Return>", self.handle_text)
        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.parent.createcommand('tk::mac::Quit', self.on_closing)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.command("/quit")

    def command(self, command):
        self.controller.handle_text(command)

    def popup(self, message):
        p_win = PopupWindow(self.parent, message)
        self.parent.wait_window(p_win.top)
        return p_win.value

    def command_arg(self, command, message):
        arg = self.popup(message)
        if arg is not None:
            self.command(command + " " + arg)

    # we call this on <Return> from the textbox
    # it behaves like the controller's main_loop
    def handle_text(self, event):
        if self.controller.ALIVE:
            text = self.textbox.get()
            self.textbox.delete(0, tk.END)
            self.controller.handle_text(text)



            
    # ----- Begin pigeon gui interface implementation -----
    
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

    # used after a hangup 
    def send_blank(self):
        self.controller.handle_text("")

    def chat_notify(self, message):
        self.chat_write(message, "SYSTEM")

    # not used, since the gui handles the main loop
    def get_text(self):
        return

    def start_gui(self, controller):
        self.controller = controller
        self.parent.after(0, self.controller.start_writing)
        self.parent.mainloop()

    def end_gui(self):
        self.parent.destroy()

    def print_userlist(self, userlist):
        self.userlist_box.configure(state="normal")
        self.userlist_box.delete(1.0, tk.END)
        for addr in userlist.keys():
            self.userlist_box.insert("end", userlist[addr] + " at " + addr + "\n")
        self.userlist_box.configure(state="disabled")

    # ----- End pigeon gui interface implementation -----

class PopupWindow:
    def __init__(self, master, message):
        self.top = tk.Toplevel(master)
        self.label = tk.Label(self.top, text=message)
        self.label.pack(side=tk.TOP)
        self.entry = tk.Entry(self.top)
        self.entry.pack(side=tk.TOP)

        self.b_frame = tk.Frame(self.top)
        self.b_frame.pack(side=tk.TOP)
        self.cancel_button = tk.Button(self.b_frame, text="Cancel", command=self.cancel)
        self.cancel_button.pack(side=tk.LEFT)
        self.ok_button = tk.Button(self.b_frame, text="Ok", command=self.cleanup)
        self.ok_button.pack(side=tk.LEFT)
        self.entry.focus_force()
        self.entry.bind("<Return>", self.cleanup)
        self.top.protocol("WM_DELETE_WINDOW", self.cancel)

    def cleanup(self, event=None):
        self.value = self.entry.get()
        self.top.destroy()

    def cancel(self, event=None):
        self.value = None
        self.top.destroy()


    
