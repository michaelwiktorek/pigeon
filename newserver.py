"""
Pigeon is a peer-to-peer chat client with end-to-end encryption.
Copyright (C) 2016 Michael Wiktorek
"""

# This server should probably only be run on a POSIX-compliant system
# otherwise some of the socket stuff might not work

import socket
import select
import threading
import signal
import json
from pigeon_constants import Pigeon_Constants as C

class Pigeon_Server:
    def __init__(self, port=None):
        # dict maps username => ip address
        self.online_users = {}
        self.connections = []
        self.userlist_lock = threading.Lock()
        self.connections_lock = threading.Lock()
        self.ALIVE = False
        self.TIMEOUT = 1
        self.HOST = ""

    # init listen socket and start main loop
    def start(self):
        self.ALIVE = True
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.server.settimeout(self.TIMEOUT)
        self.server.bind((self.HOST, C.SERVER_MAIN_PORT))
        self.server.setblocking(0)
        self.server.listen(5)
        self.connections.append(self.server)
        print "listening on port " + str(C.SERVER_MAIN_PORT)

        # here is our main server loop
        self.connect_loop()

        # TODO this may be unnecessary
        self.server.close()

    # loop on select on all open sockets
    def connect_loop(self):
        while self.ALIVE:
            reads, writes, errs = select.select(self.connections, [], self.connections)
            for conn in reads:
                self.handle_read(conn)

    # sort out new connections from data packets
    def handle_read(self, conn):
        if conn is self.server:
            self.handle_server(conn)
        else:
            self.handle_data(conn)

    # sort out filled data packets from empties (indicate disconnect)
    def handle_data(self, conn):
        data = conn.recv(2048)
        if data:
            self.handle_message(conn, data)
        else:
            self.handle_disconnect(conn)

    # handle empty packet (disconnect)
    def handle_disconnect(self, conn):
        client_addr = conn.getpeername()[0]
        print client_addr + " suddenly disconnected"
        try:
            del self.online_users[client_addr]
        except:
            print client_addr + " disconnected but was already offline... ?"
        conn.close()
        self.connections.remove(conn)

    # handle filled data packet (message from client)
    def handle_message(self, conn, data):
        user_info = data.split(":")
        print user_info
        name = user_info[0]
        mesg = user_info[1]
        client_addr = conn.getpeername()[0]
        # update online-users list
        if mesg == C.REGISTER:
            print "register from " + name + " at " + client_addr
            self.online_users[client_addr] = name
        elif mesg == C.RE_REGISTER:
            try:
                self.online_users[client_addr] = name
            except KeyError:
                print "Invalid rename from " + client_addr
        elif mesg == C.UNREGISTER:
            print "un_register from " + name + " at " + client_addr
            try:
                del self.online_users[client_addr]
            except KeyError:
                print name + " was already offline... ?"
            conn.close()
            self.connections.remove(conn)
        elif mesg == C.REQUEST:
            print "Sending userlist to " + client_addr
            userlist = json.dumps(self.online_users)
            conn.sendall(userlist)

    # handle connection request from a new client
    def handle_server(self, conn):
        new_conn, addr = conn.accept()
        print "got initial conn from " + addr[0]
        new_conn.setblocking(0)
        self.connections.append(new_conn)

    def kill_connections(self):
        for conn in self.connections:
            conn.close()

    def print_online_users(self):
        print str(len(self.online_users)) + " Users Online: "
        for addr in self.online_users.keys():
            print self.online_users[addr][0] + " at " + addr

                    
            
if __name__ == "__main__":
    server = Pigeon_Server()

    def signal_handler(*args):
        print "Quitting Pigeon Server....."
        server.ALIVE = False

    signal.signal(signal.SIGINT, signal_handler)
    
    server.start()

    print "Goodbye!"
