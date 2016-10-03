import socket
import sys
from pigeon_gui import Pigeon_GUI
from pigeon_config import Pigeon_Config
from pigeon_constants import Pigeon_Constants as C
from pigeon_register_agent import Pigeon_Register_Agent

class Communicator_Main:
    def __init__(self, config, register_agent):
        self.HOST = "127.0.0.1"
        self.config = config
        self.register_agent = register_agent
        self.connect_spawn_loop = True
        self.server_wait = True
        self.TIMEOUT = 1
        self.SERVER_TIMEOUT = 1
        self.QUIT = False

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

    # get a user instruction and call the appropriate method
    def handle_instructions(self, name):
        print "(w)ait for connection, (c)onnect, change (n)ame, (r)equest userlist, or (q)uit: "
        instruction = raw_input("(w/c/n/r/q): ")
        if instruction == "w":
            return self.wait_connection(name)
        elif instruction == "c":
            return self.attempt_connection(name)
        elif instruction == "n":
            old_name = config.name
            config.change_name_config(name)
            if self.register_agent.CONNECTED:
                self.register_agent.re_register(old_name, config.name)
            return (None, None)
        elif instruction == "q":
            self.QUIT = True
            return (None, None)
        elif instruction == "r":
            if self.register_agent.CONNECTED:
                self.register_agent.request_userlist(config.name)
                self.register_agent.print_userlist()
            else:
                print "Not connected to server"
            return (None, None)
        else:
            print "Invalid Command!"
            return (None, None)

    # start looping, taking user input
    def start(self):
        while self.connect_spawn_loop:
            # establish connection to other user
            conn, other_name = self.handle_instructions(config.name)
            if self.QUIT:
                print "Quitting....."
                return
            elif conn is not None:
                # initialize GUI with connection and names
                gui = Pigeon_GUI(conn, config.name, other_name)
                # start gui execution
                gui.start()
                # gui has died, so close connection
                conn.close()
    
if __name__ == '__main__':
    print "Pigeon is starting!"
    
    # create config object and get username
    config = Pigeon_Config()
    username = config.obtain_name()
    if len(sys.argv) > 1:
        server = sys.argv[1]
    else:
        server = C.DEFAULT_SERVER
    # create registry agent and try to register with default server
    # TODO may want to break this out into a separate function
    reg_agent = Pigeon_Register_Agent(server)
    if reg_agent.register(config.name):
        print "Registered with server at " + server + " as " + config.name
        reg_agent.request_userlist(config.name)
        reg_agent.print_userlist()
    else:
        print "Server at " + server + " unreachable, continuing without server"
        
    # create main program communicator and start it
    comm = Communicator_Main(config, reg_agent)
    comm.start()
    
    # after we're done, unregister from server
    reg_agent.unregister(config.name)

    print "Pigeon has quit!"
