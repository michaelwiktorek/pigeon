import threading
import socket
import time
import select
import curses
import curses.textpad
from Queue import Queue

class GUI:
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

        sender = threading.Thread(target=send_worker, args=(self.sock, self))
        receiver = threading.Thread(target=receive_worker, args=(self.sock, self))
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
        

class Communicator:
    def __init__(self):
        print "Pigeon is starting"
        self.PORT = 1777
        self.HOST = ""
        self.connect_loop = True
        self.TIMEOUT = 1

    def start(self):
        name = raw_input("Enter your name: ")
        while self.connect_loop:
            instruction = raw_input("Wait for a connection, attempt to Connect, or Quit (w/c/q): ")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if instruction == "w":
                print "waiting..."
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.sock.bind((self.HOST, self.PORT))
                self.sock.listen(1)
                conn, addr = self.sock.accept() # here's where we wait
                conn.settimeout(self.TIMEOUT)
                self.op_socket = conn

                #try and retrieve other user's name; first message sent
                other_name = None
                while not other_name:
                    other_name = self.op_socket.recv(1024)
                    # having received name, send our name
                self.op_socket.sendall(name)
            elif instruction == "c":
                ip = raw_input("Enter ip address: ")
                try:
                    self.sock.connect((ip, self.PORT))
                except:
                    print "Connection failed!"
                    continue
                self.sock.settimeout(self.TIMEOUT)
                self.op_socket = self.sock

                #send our name to the other user
                self.op_socket.sendall(name)
                # wait for their name in return
                other_name = None
                while not other_name:
                    other_name = self.op_socket.recv(1024)
            else:
                print "Pigeon has quit!"
                return
                

            self.gui = GUI(self.op_socket, name, other_name)
            self.gui.start()
            self.op_socket.close()
            self.sock.close()

        print "Pigeon has quit!"


def send_worker(sock, gui):
    while gui.ALIVE:
        try:
            message = gui.msg_send.get(block=True, timeout=5)
            sock.sendall(message)
            if message == gui.KILL_MSG:
                gui.display_message("You have disconnected, [ENTER] to quit", "**SYSTEM**")
                gui.ALIVE = False
        except:
            continue # we can do something here maybe


def receive_worker(sock, gui):
    while gui.ALIVE:
        try:
            message = sock.recv(1024)
            if message == gui.KILL_MSG:
                gui.display_message("Other side has disconnected, [ENTER] to quit", "**SYSTEM**")
                gui.ALIVE = False
            elif message:
                gui.display_message(message, gui.other_name)
        except:
            continue
            
        
if __name__ == '__main__':
    comm = Communicator()
    comm.start()
