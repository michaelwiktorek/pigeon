import socket
from pigeon_gui import Pigeon_GUI
from pigeon_constants import Pigeon_Constants as C

class Communicator:
    def __init__(self):
        print "Pigeon is starting"
        self.HOST = ""
        self.connect_loop = True
        self.TIMEOUT = 1

    def start(self):
        # try to read username from config file
        # if no file, then create one!
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
            
        while self.connect_loop:
            instruction = raw_input("(w)ait for connection, (c)onnect, change (n)ame, or (q)uit (w/c/n/q): ")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if instruction == "w":
                print "waiting..."
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.sock.bind((self.HOST, C.CLIENT_MAIN_PORT))
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
                    self.sock.connect((ip, C.CLIENT_MAIN_PORT))
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
            elif instruction == "n":
                try:
                    config_file = open("pigeon.conf", 'w')
                    name = raw_input("Enter your name: ")
                    config_file.write(name + "\n")
                    config_file.close()
                    print "Your name is now " + name
                except:
                    print "uh oh, something went wrong"
                continue
            else:
                print "Pigeon has quit!"
                return
                

            self.gui = Pigeon_GUI(self.op_socket, name, other_name)
            self.gui.start()
            self.op_socket.close()
            self.sock.close()

        print "Pigeon has quit!"
        
if __name__ == '__main__':
    comm = Communicator()
    comm.start()
