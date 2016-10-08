import threading
import socket
import curses
import time
import curses.textpad
from Queue import Queue
from pigeon_constants import Pigeon_Constants as C
from pigeon_threads import Pigeon_Threads

class Pigeon_GUI:
    def __init__(self, name):
        self.msg_send = Queue()
        self.commands = Queue()
        self.ALIVE = False
        self.name = name

    def start_input(self):
        self.input_loop()
        self.ALIVE = False

    def start_gui(self):
        curses.wrapper(self.initialize_elements)
       
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
        self.userlist = curses.newwin(2*scr_y/3, scr_x/3, 0, 2*scr_x/3)
        self.userlist.border()
        self.userlist.refresh()

        self.start_input()
    
    def input_loop(self):  
        #loop accepting input and echoing to the display_pad
        while self.ALIVE:
            message = self.textbox.edit()

            # put message in correct queue? probably this
            # spawn correct thread?
            
            if message.replace(" ", "").replace("\n", "") == "quit":
                self.msg_send.put(C.KILL)
                self.ALIVE = False
                #time.sleep(1)
            else:
                self.chat_pad.display_message(message, "You")
                self.msg_send.put(message)
            

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
