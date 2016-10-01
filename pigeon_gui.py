import threading
import socket
import curses
import curses.textpad
from Queue import Queue
from pigeon_threads import Pigeon_Threads

class Pigeon_GUI:
    def __init__(self, sock, name, other_name):
        self.msg_send = Queue()
        self.sock = sock
        self.KILL_MSG = "*>*>*>*>*>"
        self.ALIVE = False
        self.name = name
        self.other_name = other_name

    def start(self):
        curses.wrapper(self.initialize)
       
    def initialize(self, screen):
        self.ALIVE = True
        scr_y, scr_x = screen.getmaxyx()
        # we display chat history in the display_pad
        self.display_pad = curses.newpad(scr_y-1, scr_x)
        self.display_pad.idlok(1)
        self.display_pad.scrollok(True)
        self.scroll = 0
        # we display the message you type in the text window
        self.text_window = curses.newwin(1, scr_x, scr_y-1, 0)
        self.textbox = curses.textpad.Textbox(self.text_window, insert_mode=True)

        sender = threading.Thread(target=Pigeon_Threads.send_worker, args=(self.sock, self))
        receiver = threading.Thread(target=Pigeon_Threads.receive_worker, args=(self.sock, self))
        sender.start()
        receiver.start()

        self.function_loop(screen)
        self.ALIVE = False
        sender.join()
        receiver.join()

    def function_loop(self, screen):  
        #loop accepting input and echoing to the display_pad
        while self.ALIVE:
            message = self.textbox.edit()
            # put message into send queue
            self.msg_send.put(message)
            # for whatever reason only the empty string matches correctly?
            if message == "":
                self.msg_send.put(self.KILL_MSG)
            self.text_window.clear()
            self.text_window.move(0,0)
            self.display_message(message, "You")

    def display_message(self, message, name):
        pad_y, pad_x =self.display_pad.getmaxyx()
        curs_y, curs_x = self.display_pad.getyx()
        self.display_pad.addstr(name + ":  " + message)
        #self.display_pad.addstr(str(curs_y) + "/" + str(pad_y))
        
        if curs_y == pad_y - 1:
            self.scroll = self.scroll + 1
            self.display_pad.resize(pad_y+1, pad_x)

        self.display_pad.move(curs_y+1, 0)        
        self.display_pad.refresh(self.scroll,0, 0,0, pad_y, pad_x)
        
