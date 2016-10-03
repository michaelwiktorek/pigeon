import socket
import threading
import signal
from pigeon_constants import Pigeon_Constants as C

class Pigeon_Register_Agent:
    def __init__(self, name, server_ip):
        self.name = name
        self.HOST = "127.0.0.1"
        self.server_ip = server_ip
        self.MAX_ATTEMPTS = 3
        self.ALIVE = True
        
    def change_name(self, new_name):
        self.name = new_name
        # might need to unregister and then re-register here
        # also update reg/unreg messages

    def send_wait_ack(self, message):
        send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # send message, await ack and resend message until ack
        send_sock.sendto(message, (self.server_ip, C.SERVER_MAIN_PORT))
        attempts_made = 0
        while attempts_made < self.MAX_ATTEMPTS:
            try:
                mesg, addr = send_sock.recvfrom(1024)
                if mesg == C.ACK:
                    print "Server acknowledges message"
                    return True
            except:
                print "Did not receive server acknowledgement, trying again..."
                continue
        return False
        send_sock.close()

    def keep_alive(self):
        test_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        test_sock.bind((self.HOST, C.CLIENT_TEST_PORT))
        test_sock.settimeout(2)
        while self.ALIVE:   # TODO figure out how to kill this
            try:
                mesg, addr = test_sock.recvfrom(1024)
                if mesg == C.TEST:
                    test_sock.sendto(C.ACK, (addr[0], addr[1]))
            except:
                continue


    def register(self):
        self.send_wait_ack(self.name + ":" + C.REGISTER)

    def unregister(self):
        self.send_wait_ack(self.name + ":" + C.UNREGISTER)


if __name__ == "__main__":
    agent = Pigeon_Register_Agent("mikey", "127.0.0.1")
    def signal_handler(*args):
        agent.ALIVE = False
    signal.signal(signal.SIGINT, signal_handler)
    alive_thread = threading.Thread(target=agent.keep_alive)
    alive_thread.start()
        
