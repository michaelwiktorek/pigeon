import socket
from pigeon_gui import Pigeon_GUI
from pigeon_constants import Pigeon_Constants as C
from pigeon_register_agent import Pigeon_Register_Agent

class Communicator_Main:
    def __init__(self):
        print "Pigeon is starting"
        self.HOST = "127.0.0.1"
        self.connect_spawn_loop = True
        self.server_wait = True
        self.TIMEOUT = 1
        self.SERVER_TIMEOUT = 1
        self.QUIT = False

    # attempt to read name from config file
    # if no file exists, create it
    def read_write_config(self):
        name = ""
        try:
            config_file = open("pigeon.conf", 'r')
            print "Reading configuration file..."
            name = config_file.readline().replace("\n", "")
            config_file.close()
            print "Your name is " + name
        except:
            print "No configuration file found, creating..."
            config_file = open("pigeon.conf", 'w')
            name = raw_input("Enter your name: ")
            config_file.write(name + "\n")
            config_file.close()
            print "Your name is now " + name
        return name

    # listen for other user's name on socket
    def recv_other_name(self, sock):
        other_name = None
        while not other_name:
            # TODO maybe stop after a few tries
            other_name = sock.recv(1024)
        return other_name

    # wait for a connection, and send our name on it
    def wait_connection(self, name):
        print "waiting..."
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.HOST, C.CLIENT_MAIN_PORT))
        sock.listen(1)
        # wait for an incoming connection
        # TODO loop on timeout, allow user to kill
        sock.settimeout(self.SERVER_TIMEOUT)
        self.server_wait = True
        conn = None
        while self.server_wait:
            try:
                conn, addr = sock.accept()
                self.server_wait = False
            except:
                continue
        # close original listen socket
        sock.close()
        # if no connection was established, return failure
        if conn is None:
            print "No connection established"
            return (None, None)
        conn.settimeout(self.TIMEOUT)
        # wait for other user's name
        other_name = self.recv_other_name(conn)
        # send our name back to other user
        conn.sendall(name)
        return (conn, other_name)

    # attempt to make a connection, and send our name on it
    def attempt_connection(self, name):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip = raw_input("Enter ip address: ")
        try:
            sock.connect((ip, C.CLIENT_MAIN_PORT))
        except:
            print "Connection failed!"
            # return None tuple on failure
            sock.close()
            return (None, None)
        sock.settimeout(self.TIMEOUT)

        #send our name to the other user
        sock.sendall(name)
        # wait for their name in return
        other_name = self.recv_other_name(sock)
        return (sock, other_name)

    # change our name in the configuration file
    def change_name_config(self, name):
        try:
            config_file = open("pigeon.conf", 'w')
            name = raw_input("Enter your name: ")
            config_file.write(name + "\n")
            config_file.close()
            print "Your name is now " + name
        except:
            print "Error changing config file!"

    # get a user instruction and call the appropriate method
    def handle_instructions(self, name):
        instruction = raw_input("(w)ait for connection, (c)onnect, change (n)ame, or (q)uit (w/c/n/q): ")
        if instruction == "w":
            return self.wait_connection(name)
        elif instruction == "c":
            return self.attempt_connection(name)
        elif instruction == "n":
            self.change_name_config(name)
            return (None, None)
        elif instruction == "q":
            self.QUIT = True
            return (None, None)
        else:
            return (None, None)

    # start looping, taking user input
    def start(self):
        # try to read username from config file
        # if no file, then create one!
        name = self.read_write_config()
            
        while self.connect_spawn_loop:
            # establish connection to other user
            conn, other_name = self.handle_instructions(name)
            if self.QUIT:
                print "Pigeon has quit!"
                return
            elif conn is not None:
                # initialize GUI with connection and names
                gui = Pigeon_GUI(conn, name, other_name)
                # start gui execution
                gui.start()
                # gui has died, so close connection
                conn.close()
        
if __name__ == '__main__':
    comm = Communicator_Main()
    comm.start()
