import socket
import sys
import signal
from pigeon_gui import Pigeon_GUI
from pigeon_config import Pigeon_Config
from pigeon_constants import Pigeon_Constants as C
from pigeon_register_agent import Pigeon_Register_Agent

class Communicator:
    def __init__(self, config, register_agent):
        self.HOST = ""
        self.config = config
        self.register_agent = register_agent
        self.connect_spawn_loop = True
        self.server_wait = True
        self.TIMEOUT = 1
        self.SERVER_TIMEOUT = 1
        self.THREAD_STAY_ALIVE = False
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
            return (None, None)
        conn.settimeout(self.TIMEOUT)
        # wait for other user's name
        other_name = self.recv_other_name(conn)
        # send our name back to other user
        conn.sendall(name)
        return (conn, other_name)

    # attempt to make a connection, and send our name on it
    def attempt_connection(self, name, ip):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.HOST, C.CLIENT_MAIN_PORT))
        sock.settimeout(1)
        if self.register_agent.CONNECTED:
            if len(ip.split(".")) != 4:
                # this is a name, not an IP, so search userlist
                for addr in self.register_agent.userlist.keys():
                    if self.register_agent.userlist[addr][0] == ip:
                        ip = addr
        try:
            sock.connect((ip, C.CLIENT_MAIN_PORT))
        except:
            # return None tuple on failure
            sock.close()
            return (None, None)
        sock.settimeout(self.TIMEOUT)

        #send our name to the other user
        sock.sendall(name)
        # wait for their name in return
        other_name = self.recv_other_name(sock)
        return (sock, other_name)
