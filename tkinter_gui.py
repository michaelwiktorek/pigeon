import Tkinter as tk
from Queue import Queue

class Tkinter_Gui:

    def __init__(self):
        self.HANDLES_MAIN_LOOP = True
        
        self.parent = tk.Tk()

        self.user_text = Queue()
        self.controller = None
    
        self.container1 = tk.Frame(self.parent)
        self.container1.pack()

        #self.button2 = tk.Button(self.container1, text="Quit", command=self.button2_click)
        #self.button2.pack(side=tk.TOP)

        self.system_box = tk.Text(self.container1, state="disabled")
        self.system_box.pack(side=tk.TOP)

        self.chat_box = tk.Text(self.container1, state="disabled")
        self.chat_box.pack(side=tk.TOP)

        #self.userlist_box = tk.Text(self.container1)
        #self.userlist_box.pack(side=tk.LEFT)

        self.textbox = tk.Entry(self.container1)
        self.textbox.pack(side=tk.TOP)
        #self.textbox.bind("<Return>", self.write_junk)
        self.textbox.bind("<Return>", self.handle_text)
        self.textbox.focus_force()

    def button2_click(self):
        print "tkinter gui has quit, lol"
        self.parent.destroy()

    # DELET THIS
    def write_junk(self, event):
        text = self.textbox.get()
        self.sys_write(text)
        self.textbox.delete(0, tk.END)

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
        return

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
