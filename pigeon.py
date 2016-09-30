import threading
import socket
import time
import curses
import curses.textpad
from Queue import Queue

class GUI:
    def __init__(self):
        self.msg_send = Queue()
       
    def start(self):
        curses.wrapper(self.operate)

    def operate(self, screen):
        scr_y, scr_x = screen.getmaxyx()
        # we display chat history in the display_pad
        self.display_pad = curses.newpad(scr_y-1, scr_x)
        self.display_pad.idlok(1)
        self.display_pad.scrollok(True)
        self.scroll = 0
        # we display the message you type in the text window
        text_window = curses.newwin(1, scr_x, scr_y-1, 0)
        textbox = curses.textpad.Textbox(text_window, insert_mode=True)
        
        #loop accepting input and echoing to the display_pad
        while True:
            message = textbox.edit()
            # put message into send queue
            self.msg_send.put(message, block=True, timeout=5)
            # for whatever reason only the empty string matches correctly?
            if message == "":
                break
            text_window.clear()
            text_window.move(0,0)
            self.display_message(message, "You")

    def display_message(self, message, name):
        pad_y, pad_x =self.display_pad.getmaxyx()
        curs_y, curs_x = self.display_pad.getyx()
        self.display_pad.addstr(name + ":  " + message)
        self.display_pad.addstr(str(curs_y) + "/" + str(pad_y))
        
        if curs_y == pad_y - 1:
            self.scroll = self.scroll + 1
            self.display_pad.resize(pad_y+1, pad_x)

        self.display_pad.move(curs_y+1, 0)        
        self.display_pad.refresh(self.scroll,0, 0,0, pad_y, pad_x)
        

class Communicator:
    def __init__(self):
        print "Pigeon is starting"
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.PORT = 1776
        self.HOST = ""
        self.AM_SERVER = False
        self.gui = GUI()

    def start(self):
        instruction = raw_input("Wait for a connection, or attempt to Connect (w/c): ")
        if instruction == "w":
            print "waiting..."
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.HOST, self.PORT))
            self.sock.listen(1)
            self.conn, self.addr = self.sock.accept() # here's where we wait
            sender = threading.Thread(target=send_worker, args=(self.conn, self.gui))
            receiver = threading.Thread(target=receive_worker, args=(self.conn, self.gui))
        else:
            ip = raw_input("Enter ip address: ")
            self.sock.connect((ip, self.PORT))
            # we have now established a connection
            # we can send and receive on this connection
            sender = threading.Thread(target=send_worker, args=(self.sock, self.gui))
            receiver = threading.Thread(target=receive_worker, args=(self.sock, self.gui))
            
        self.gui.start()
        sender.start()
        receiver.start()
        sender.join()
        self.sock.close()
        receiver.join()

        print "pigeon has experienced the sweet release of death"


def send_worker(sock, gui):
    running = True
    while running == True:
        try:
            message = gui.msg_send.get(block=True, timeout=5)
            sock.sendall(message)
            if message == "":
                running = False
        except:
            continue # we can do something here maybe


def receive_worker(sock, gui):
    running = True
    while running == True:
        message = sock.recv(1024)
        if message:
            gui.display_message(message, "Them")
        else:
            running = False
                
        
if __name__ == '__main__':
    # start by asking the user whether to oh god none of this works
    # we go full P2P
    # start program
    # option to send connect request
    # if request received, then spin up sender thread, connect to origin

    # all garbage, see ideas.txt
    
    comm = Communicator()
    comm.start()
