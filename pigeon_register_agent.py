import socket
import threading
import signal
from pigeon_constants import Pigeon_Constants as C

class Pigeon_Register_Agent:
    def __init__(self, server_ip):
        self.CONNECTED = False
        self.HOST = "127.0.0.1"
        self.server_ip = server_ip
        self.MAX_ATTEMPTS = 3
        self.ALIVE = True
        
    def send_wait_ack(self, message):
        send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # send message, await ack and resend message until ack
        send_sock.sendto(message, (self.server_ip, C.SERVER_MAIN_PORT))
        attempts_made = 0
        while attempts_made < self.MAX_ATTEMPTS:
            try:
                mesg, addr = send_sock.recvfrom(1024)
                if mesg == C.ACK:
                    send_sock.close()
                    print "Server acknowledges " + message
                    return True
            except:
                print "Did not receive server acknowledgement, trying again..."
                continue
        send_sock.close()
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

    # unregister and re-register without killing keepalive thread
    def re_register(self, old_name, new_name):
        self.send_wait_ack(old_name + ":" + C.UNREGISTER)
        self.send_wait_ack(new_name + ":" + C.REGISTER)


    def register(self, name):
        if self.send_wait_ack(name + ":" + C.REGISTER):
            self.ALIVE = True
            self.CONNECTED = True
            self.keep_alive_thread = threading.Thread(target=self.keep_alive)
            self.keep_alive_thread.start()
            return True
        else:
            return False

    def unregister(self, name):
        self.ALIVE = False
        self.CONNECTED = False
        return self.send_wait_ack(name + ":" + C.UNREGISTER)

if __name__ == "__main__":
    agent = Pigeon_Register_Agent("127.0.0.1")
    def signal_handler(*args):
        agent.ALIVE = False
    signal.signal(signal.SIGINT, signal_handler)
        
