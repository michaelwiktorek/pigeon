class Pigeon_Threads:

    @staticmethod
    def send_worker(sock, gui):
        while gui.ALIVE:
            try:
                message = gui.msg_send.get(block=True, timeout=5)
                sock.sendall(message)
                if message == gui.KILL_MSG:
                    gui.display_message("You have disconnected, [ENTER] to quit", "**SYSTEM**")
                    gui.ALIVE = False
            except:
                continue # we can do something here maybe

    @staticmethod
    def receive_worker(sock, gui):
        while gui.ALIVE:
            try:
                message = sock.recv(1024)
                if message == gui.KILL_MSG:
                    gui.display_message("Other side has disconnected, [ENTER] to quit", "**SYSTEM**")
                    gui.ALIVE = False
                elif message:
                    gui.display_message(message, gui.other_name)
            except:
                continue
