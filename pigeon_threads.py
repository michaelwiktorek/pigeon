from pigeon_constants import Pigeon_Constants as C

class Pigeon_Threads:

    @staticmethod
    def send_worker(sock, controller):
        rsa = controller.communicator.rsa
        while controller.communicator.THREAD_STAY_ALIVE:
            try:
                message = controller.msg_send.get(block=True, timeout=1)
                # we could try send/recv public keys here
                if message != C.KILL:
                    msg_cipher = rsa.encipher_long_str(message)
                else:
                    msg_cipher = message
                sock.sendall(msg_cipher)
            except:
                continue # we can do something here maybe

    @staticmethod
    def receive_worker(sock, controller, other_name):
        gui = controller.gui
        rsa = controller.communicator.rsa
        while controller.communicator.THREAD_STAY_ALIVE:
            try:
                message = sock.recv(2048)
                if message == C.KILL:
                    gui.chat_notify("Other side has disconnected, hit [ENTER] to leave")
                    controller.HANGUP = True
                elif message:
                    message_decrypt = rsa.decipher_long_str(message)
                    gui.chat_write(message_decrypt, other_name)
            except:
                continue
