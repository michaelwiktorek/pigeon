import socket
import threading
import signal
import sys
import time
import json
from pigeon_constants import Pigeon_Constants as C

class Pigeon_Server:
    def __init__(self, port=None):
        # dict maps username => ip address
        self.online_users = {}
        self.userlist_lock = threading.Lock()
        self.ALIVE = False
        self.TIMEOUT = 1
        self.HOST = ""

    def start(self):
        self.ALIVE = True
        #self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(self.TIMEOUT)
        self.sock.bind((self.HOST, C.SERVER_MAIN_PORT))
        #self.sock.listen(5)
        print "listening on port " + str(C.SERVER_MAIN_PORT)

        # here we need to start our user-pruning thread
        pruning_thread = threading.Thread(target=self.prune_users)
        pruning_thread.start()
        
        self.recv_loop_UDP()
        pruning_thread.join()

    def print_online_users(self):
        print str(len(self.online_users)) + " Users Online: "
        for addr in self.online_users.keys():
            print self.online_users[addr][0] + " at " + addr

    def prune_users(self):
        while self.ALIVE:
            self.userlist_lock.acquire()
            print "pruning offline users"
            prune_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # bind to server main port (is this allowed?)  NO
            prune_socket.bind((self.HOST, C.SERVER_REGISTER_PORT))
            prune_socket.settimeout(2) # allow 2 secs for a response
            # THIS COULD BE VERY WEIRD WITH THREADS, LOOK INTO IT
            # mark unresponsive clients for deletion
            for addr in self.online_users.keys():
                prune_socket.sendto(C.TEST, (addr, C.CLIENT_TEST_PORT))
                try:
                    mesg, addr = prune_socket.recvfrom(1024)
                    if mesg == C.ACK:
                        # update time # actually don't
                        #self.online_users[addr][1] = time.time()
                        print self.online_users[addr][0] + " is still online"
                        continue
                except:
                    self.online_users[addr] = None
                    
            # close socket
            prune_socket.close()

            # remove unresponsive clients from list
            for addr in self.online_users.keys():
                if self.online_users[addr] is None:
                    del self.online_users[addr]

            self.print_online_users()
            self.userlist_lock.release()
            
            # is this idiotic? I think so
            for i in range(C.ONLINE_TIMEOUT_SECS):
                if not self.ALIVE:
                    break  # let me die
                time.sleep(1)
        print "pruning thread has died"

    def recv_loop_UDP(self):
        while self.ALIVE:
            try:
                data, addr = self.sock.recvfrom(1024)
            except:
                continue
            client_port = addr[1]
            client_addr = addr[0]
            user_info = data.split(":")
            name = user_info[0]
            mesg = user_info[1]
            # update online-users list
            self.userlist_lock.acquire()
            if mesg == C.REGISTER:
                print "register from " + name + " at " + client_addr
                self.online_users[client_addr] = name, time.time()
                self.send_ack(addr)
            elif mesg == C.UNREGISTER:
                print "UNregister from " + name + " at " + client_addr
                self.send_ack(addr)
                try:
                    del self.online_users[client_addr]
                except KeyError:
                    print "User is already offline!"
            elif mesg == C.REQUEST:
                # serialize and send userlist to client
                userlist = json.dumps(self.online_users)
                list_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                list_sock.sendto(userlist, (client_addr, client_port))
                list_sock.close()
            else:
                continue # not strictly necessary
            
            self.print_online_users()
            self.userlist_lock.release()
            
        self.sock.close()

    def send_ack(self, address):
        print ""
        print "sending ack to " + address[0] + ":" + str(address[1])
        print ""
        ack_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ack_sock.sendto(C.ACK, (address[0], address[1]))
        ack_sock.close()

                    
            
if __name__ == "__main__":
    server = Pigeon_Server()

    def signal_handler(*args):
        print "Attempting to kill Pigeon server...."
        server.ALIVE = False

    signal.signal(signal.SIGINT, signal_handler)
    
    server.start()

    print "Prune thread joined, main thread dying now!"
