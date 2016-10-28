"""
Pigeon is a peer-to-peer chat client with end-to-end encryption.
Copyright (C) 2016 Michael Wiktorek
"""

import socket
import sys
import signal
from pigeon_config         import Pigeon_Config
from pigeon_constants      import Pigeon_Constants as C
from pigeon_register_agent import Pigeon_Register_Agent
from rsa                   import RSA

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
        self.rsa = RSA()

    # listen for other user's name on socket
    def recv_other_data(self, sock):
        other_data = None
        while not other_data:
            # TODO maybe stop after a few tries
            other_data = sock.recv(1024)
        split_data = other_data.split(":")
        other_name = split_data[0]
        pubkey = (int(split_data[1]), int(split_data[2]))
        return (other_name, pubkey)

    # get an rsa object god this needs refactoring, also gen keypair
    def rsa_gen_keypair(self):
        self.rsa.gen_keypair()
        self.n, self.e = self.rsa.get_public_key()

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
        other_name, pub_key = self.recv_other_data(conn)
        self.rsa.get_other_pub_key(pub_key)
        # send our name back to other user
        data = name + ":" + str(self.n) + ":" + str(self.e)
        conn.sendall(data)
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

        #send data to the other user
        data = name + ":" + str(self.n) + ":" + str(self.e)
        sock.sendall(data)
        # wait for their name in return
        other_name, pub_key = self.recv_other_data(sock)
        self.rsa.get_other_pub_key(pub_key)
        return (sock, other_name)
