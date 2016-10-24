from pigeon_constants import Pigeon_Constants as C

class Pigeon_Threads:

    @staticmethod
    def send_worker(sock, gui):
        while gui.communicator.THREAD_STAY_ALIVE:
            try:
                message = gui.msg_send.get(block=True, timeout=1)
                # we could try send/recv public keys here
                sock.sendall(message)
                #if message == C.KILL:
                    #gui.chat_pad.display_message("You have disconnected, goodbye!", "**SYSTEM**")
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
                    gui.chat_pad.display_message(message, gui.other_name)
            except:
                continue
