"""
Pigeon is a peer-to-peer chat client with end-to-end encryption.
Copyright (C) 2016 Michael Wiktorek
"""

import socket
import sys
import threading
import signal
import json
from pigeon_constants import Pigeon_Constants as C

class Pigeon_Register_Agent:
    def __init__(self):
        self.userlist = {}
        self.CONNECTED = False
        self.HOST = ""
        self.server_ip = C.DEFAULT_SERVER
        self.MAX_ATTEMPTS = 1
        self.TIMEOUT = 1

    def set_server_ip(self, ip):
        self.server_ip = ip
        
    def establish_conn(self):
        try:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.settimeout(self.TIMEOUT)
            self.conn.connect((self.server_ip, C.SERVER_MAIN_PORT))
            return True
        except:
            return False
        
    def close_conn(self):
        self.conn.close()

    def send_message(self, message):
        try:
            self.conn.sendall(message)
            return True
        except:
            return False

    def get_response(self):
        attempts_made = 0
        while attempts_made < self.MAX_ATTEMPTS:
            try:
                return self.conn.recv(2048)
            except:
                attempts_made += 1
                continue
        return None

    def request_userlist(self, name):
        # return deserialized json userlist
        if self.send_message(name + ":" + C.REQUEST):
            response = self.get_response()
            if response:
                self.userlist = json.loads(response)
                return True
        return False

    def re_register(self, new_name):
        self.send_message(new_name + ":" + C.RE_REGISTER)

    def register(self, name):
        if self.establish_conn() and self.send_message(name + ":" + C.REGISTER):
            self.CONNECTED = True
            return True
        else:
            return False

    def unregister(self, name):
        # only send an unregister message if we registered successfully
        if self.CONNECTED:
            self.CONNECTED = False
            self.send_message(name + ":" + C.UNREGISTER)
            self.close_conn()
        else:
            return False
        
