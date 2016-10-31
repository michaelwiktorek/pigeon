"""
Pigeon is a peer-to-peer chat client with end-to-end encryption.
Copyright (C) 2016 Michael Wiktorek
"""

from pigeon_constants import Pigeon_Constants as C

class Pigeon_Threads:

    @staticmethod
    def send_worker(sock, controller):
        rsa = controller.communicator.rsa
        while controller.communicator.THREAD_STAY_ALIVE:
            try:
                message = controller.msg_send.get(block=True, timeout=1)
                # we could try send/recv public keys here
                if message == C.KILL or message.split("|")[0] == C.RENAME:
                    msg_cipher = message
                else:
                    msg_cipher = rsa.encipher_long_str(message)
                sock.sendall(msg_cipher)
            except:
                continue # we can do something here maybe

    @staticmethod
    def receive_worker(sock, controller, other_name):
        convo_name = other_name
        gui = controller.gui
        rsa = controller.communicator.rsa
        while controller.communicator.THREAD_STAY_ALIVE:
            try:
                message = sock.recv(2048)
                if message == C.KILL:
                    controller.HANGUP = True
                    gui.chat_notify("Other side has disconnected, hit [ENTER] to acknowledge")
                elif message.split("|")[0] == C.RENAME:
                    # other user has sent rename message
                    convo_name = message.split("|")[1]
                    gui.chat_notify("Other side changed name to " + convo_name)
                elif message:
                    message_decrypt = rsa.decipher_long_str(message)
                    gui.chat_write(message_decrypt, convo_name)
            except:
                continue
