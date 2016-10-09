import threading
import socket
import curses
import time
import curses.textpad
from Queue import Queue
from pigeon_constants import Pigeon_Constants as C
from pigeon_threads import Pigeon_Threads

class Pigeon_GUI:
    def __init__(self, config, register, communicator):
        self.msg_send = Queue()
        self.commands = Queue()
        self.ALIVE = False
        self.config = config
        self.register = register
        self.communicator = communicator
        self.in_conversation = False
        self.HANGUP = False

    def start_input(self):
        self.input_loop()
        self.ALIVE = False

    def start_gui(self):
        curses.wrapper(self.initialize_elements)

    def print_userlist(self, window):
        self.userlist_win.border()
        for addr in self.register.userlist.keys():
            self.userlist_win.addstr(self.register.userlist[addr][0] + " at " + addr)
            curs_y, curs_x = self.userlist_win.getyx()
            self.userlist_win.move(curs_y+1, 0)
        self.userlist_win.refresh()

    def start_convo(self, conn, other_name):
        self.in_conversation = True
        self.communicator.THREAD_STAY_ALIVE = True
        self.other_name = other_name
        sender = threading.Thread(target=Pigeon_Threads.send_worker, args=(conn, self))
        sender.start()
        Pigeon_Threads.receive_worker(conn, self)
        sender.join()
    
    def connect_background(self, ip):
        conn, other_name = self.communicator.attempt_connection(self.name, ip)
        if conn:
            self.start_convo(self, conn, other_name)
            conn.close()
        else:
            self.display_pad.display_message("Failed to connect to " + ip, "SYSTEM")
            # notify user of failure to connect

    def wait_connection_background(self):
        conn, other_name = self.communicator.wait_connection(self.name)
        if conn:
            self.start_convo(self, conn, other_name)
            conn.close()
       
    def initialize_elements(self, screen):
        self.ALIVE = True
        scr_y, scr_x = screen.getmaxyx()
        
        # we display chat history in the display_pad
        self.chat_pad = Scroll_Pad(2*scr_y/3, 2*scr_x/3, 0, 0)
        
        # we display system messages in the system window
        self.system_pad = Scroll_Pad(2*scr_y/3, 2*scr_x/3, 0, 0)
        
        # we display the message you type in the text window
        self.textbox = Simple_Textbox(3, scr_x, scr_y-3, 0)

        # display current list of users, maybe some commands
        self.userlist_win = curses.newwin(2*scr_y/3, scr_x/3, 0, 2*scr_x/3)
        self.userlist_win.leaveok(0)
        self.userlist_win.border()
        self.userlist_win.refresh()

        self.config.get_gui(self)
        self.name = self.config.obtain_name()

        self.register.get_gui(self)
        self.register.register(self.name)

        # init wait_connection_background here
        self.conn_thread = threading.Thread(target=self.wait_connection_background) #stupid, needed?
        self.wait_conn_thread = threading.Thread(target=self.wait_connection_background)
        self.wait_conn_thread.start()
        
        self.start_input()
    
    def input_loop(self):  
        #loop accepting input and echoing to the display_pad
        while self.ALIVE:
            message = self.textbox.edit()

            if self.HANGUP:
                self.HANGUP = False
                self.in_conversation = False
                self.communicator.THREAD_STAY_ALIVE = False
                # join on any conversation thread
                if self.wait_conn_thread.isAlive():
                    self.wait_conn_thread.join()
                elif self.conn_thread.isAlive():
                    self.conn_thread.join()
                # start new wait_connection_background thread
                self.wait_conn_thread = threading.Thread(target=self.wait_connection_background)
                self.wait_conn_thread.start()
                self.system_pad.display("Chat ended at " + time.ctime(time.time()), "SYSTEM")
            
            if message[0] == "/":
                cmd = message.replace(" ", "").replace("\n", "")
                if cmd  == "/quit":
                    self.msg_send.put(C.KILL)
                    if self.register.CONNECTED:
                        self.register.unregister(self.name)
                    self.communicator.server_wait = False
                    self.communicator.THREAD_STAY_ALIVE = False
                    # join on conversation threads
                    if self.wait_conn_thread.isAlive():
                        self.wait_conn_thread.join()
                    elif self.conn_thread.isAlive():
                        self.conn_thread.join()
                    self.system_pad.display_message("Quitting.... goodbye!", "SYSTEM")
                    self.ALIVE = False
                    #time.sleep(1)
                elif cmd == "/rename":
                    old_name = self.name
                    self.name = self.config.change_name_config()
                    if self.register.CONNECTED:
                        self.register.re_register(old_name, self.name)
                elif cmd == "/connect":
                    # communicator needs to say this
                    if not self.in_conversation:
                        self.system_pad.display_message("Enter an IP or name", "SYSTEM")
                        other = self.textbox.edit()
                        # we want to spawn a thread here
                        # to do connect_background
                        self.THREAD_STAY_ALIVE = False         # kill threads just in case
                        self.communicator.server_wait = False  # stop comm.wait_connection
                        self.wait_conn_thread.join()           # join wait thread
                        self.conn_thread = threading.Thread(target=self.connect_background, args=(other,))
                        #self.system_pad.display_message("Can't connect to " + other, "SYSTEM")
                        self.conn_thread.start()
                    else:
                        continue
                elif cmd == "/hangup":
                    if self.in_conversation:
                        self.msg_send.put(C.KILL)
                        # TODO this might kill send threat too early?
                        #self.communicator.THREAD_STAY_ALIVE = False
                        self.HANGUP = True
                        self.chat_pad.display("You have disconnected, hit [ENTER] to leave", "SYSTEM")
                    else:
                        continue
                elif cmd == "/online":
                    self.register.request_userlist(self.name)
                    self.userlist_win.clear()
                    self.print_userlist(self.userlist_win)
                    self.system_pad.display_message("Userlist updated!", "SYSTEM")
                elif cmd == "/register":
                    # TODO crashes if you enter improper address format
                    self.system_pad.display_message("Type an IP address and hit [ENTER]", "SYSTEM")
                    ip = self.textbox.edit()
                    if self.register.CONNECTED:
                        self.register.unregister(self.name)
                    self.register.set_server_ip(ip)
                    self.register.register(self.name)
                elif cmd == "/unregister":
                    self.register.unregister(self.config.name)
                    self.system_pad.display_message("Logged out of " + self.register.server_ip, "REGISTER")
                else:
                    self.system_pad.display_message("Invalid command!", "SYSTEM")
                    
            else:
                if self.in_conversation:
                    self.chat_pad.display_message(message, "You")
                    self.msg_send.put(message)
                else:
                    continue
                    #self.system_pad.display_message(message, "You")
                    #self.msg_send.put(message)
            

class Scroll_Pad:
    def __init__(self, nrow, ncol, y, x):
        self.display = curses.newpad(nrow, ncol)
        self.scroll = 0
        self.y = y
        self.x = x
        self.nrow = nrow
        self.ncol = ncol
        self.display.border()
        self.display.idlok(1)
        self.display.scrollok(True)
        self.display.leaveok(0)
        self.refresh()
        
    def refresh(self):
        self.display.refresh(self.scroll, 0, self.y, self.x, self.nrow, self.ncol)

    def display_message(self, message, name):
        curs_y, curs_x = self.display.getyx()
        self.display.addstr(name + ": " + message)
        if curs_y == self.nrow - 1:
            self.scroll = self.scroll + 1
            self.nrow = self.nrow + 1
            self.display.resize(self.nrow + 1, self.ncol)
        curs_y, curs_x = self.display.getyx()
        self.display.move(curs_y+1, 0)
        self.refresh()

class Simple_Textbox:
    def __init__(self, nrow, ncol, y, x):
        self.y = y
        self.x = x
        self.nrow = nrow
        self.ncol = ncol
        self.win = curses.newwin(nrow, ncol, y, x)

    # holy crap what a pile of steaming garbage TODO pls help
    def edit(self):
        str = []
        while True:
            ch = self.win.getch()
            if ch == C.ENTER:    # ENTER
                self.win.clear()
                self.win.move(0,0)
                self.win.refresh()
                return "".join(str)
            elif ch == C.DEL or ch == C.DEL_2:  # DELETE
                curs_y, curs_x = self.win.getyx()
                win_y, win_x = self.win.getmaxyx()
                # garbage move cursor
                if curs_x > 0:
                    str.pop()
                    self.win.move(curs_y, curs_x-1)
                elif curs_y >= 1:
                    str.pop()
                    self.win.move(curs_y-1, win_x-1)
                    
                self.win.delch()
            else:          # OTHER CHARACTER
                curs_y, curs_x = self.win.getyx()
                win_y, win_x = self.win.getmaxyx()
                if curs_x == win_x-1:
                    if curs_y < win_y-1:
                        self.win.addch(chr(ch))
                        str.append(chr(ch))
                        self.win.move(curs_y + 1, 0)
                else:
                    self.win.addch(chr(ch))
                    str.append(chr(ch))
                    self.win.move(curs_y, curs_x + 1)
                self.win.refresh()
