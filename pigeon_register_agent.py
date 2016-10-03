import socket
import sys
import threading
import signal
import json
from pigeon_constants import Pigeon_Constants as C

class Pigeon_Register_Agent:
    def __init__(self, server_ip):
        self.userlist = {}
        self.CONNECTED = False
        self.HOST = ""
        self.server_ip = server_ip
        self.MAX_ATTEMPTS = 3
        self.ALIVE = True
        
    def send_wait_ack(self, message):
        send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # send message, await ack and resend message until ack
        send_sock.sendto(message, (self.server_ip, C.SERVER_MAIN_PORT))
        send_sock.settimeout(1)
        attempts_made = 0
        #sys.stdout.write("Sending " + message + " to server")
        #sys.stdout.flush()
        while attempts_made < self.MAX_ATTEMPTS:
            try:
                attempts_made = attempts_made + 1
                mesg, addr = send_sock.recvfrom(1024)
                if mesg == C.ACK:
                    send_sock.close()
                    #print "\nServer acknowledges " + message
                    attempts_made = 0
                    return True
                else:
                    send_sock.close()
                    #print "\nServer acknowledges " + message
                    attempts_made = 0
                    return mesg
            except:
                sys.stdout.write(".")
                sys.stdout.flush()
                continue
        send_sock.close()
        attempts_made = 0
        print ""
        return False

    def keep_alive(self):
        test_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        test_sock.bind((self.HOST, C.CLIENT_TEST_PORT))
        test_sock.settimeout(1)
        while self.ALIVE:
            try:
                mesg, addr = test_sock.recvfrom(1024)
                if mesg == C.TEST:
                    test_sock.sendto(C.ACK, (addr[0], addr[1]))
            except:
                continue
        test_sock.close()

    def request_userlist(self, name):
        # return deserialized json userlist
        mesg = self.send_wait_ack(name + ":" + C.REQUEST)
        if mesg:
            self.userlist = json.loads(mesg)
            return True
        else:
            return False

    def print_userlist(self):
        for addr in self.userlist.keys():
            print self.userlist[addr][0] + " online at " + addr
        
    # unregister and re-register without killing keepalive thread
    def re_register(self, old_name, new_name):
        self.send_wait_ack(old_name + ":" + C.UNREGISTER)
        self.send_wait_ack(new_name + ":" + C.REGISTER)


    def register(self, name):
        if self.send_wait_ack(name + ":" + C.REGISTER):
            self.ALIVE = True
            self.CONNECTED = True
            #print "Starting keep_alive thread at port " + str(C.CLIENT_TEST_PORT)
            self.keep_alive_thread = threading.Thread(target=self.keep_alive)
            self.keep_alive_thread.start()
            return True
        else:
            return False

    def unregister(self, name):
        self.ALIVE = False
        # only send an unregister message if we registered successfully
        if self.CONNECTED:
            self.CONNECTED = False
            return self.send_wait_ack(name + ":" + C.UNREGISTER)
        else:
            return False

if __name__ == "__main__":
    agent = Pigeon_Register_Agent("127.0.0.1")
    def signal_handler(*args):
        agent.ALIVE = False
    signal.signal(signal.SIGINT, signal_handler)
        
