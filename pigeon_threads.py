from pigeon_constants import Pigeon_Constants as C

class Pigeon_Threads:

    @staticmethod
    def send_worker(sock, gui):
        while gui.communicator.THREAD_STAY_ALIVE:
            try:
                message = gui.msg_send.get(block=True, timeout=1)
                # we could try send/recv public keys here
                if message != C.KILL:
                    msg_cipher = str(gui.rsa.encrypt_known(message))
                else:
                    msg_cipher = message
                sock.sendall(msg_cipher)
            except:
                continue # we can do something here maybe

    @staticmethod
    def receive_worker(sock, gui):
        while gui.communicator.THREAD_STAY_ALIVE:
            try:
                message = sock.recv(1024)
                if message == C.KILL:
                    gui.chat_pad.display_message("Other side has disconnected, hit [ENTER] to leave", "SYSTEM")
                    gui.HANGUP = True
                elif message:
                    message_decrypt = gui.rsa.decrypt(int(message))
                    gui.chat_pad.display_message(message_decrypt, gui.other_name)
            except:
                continue
