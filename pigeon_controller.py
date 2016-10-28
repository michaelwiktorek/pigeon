import threading
import time
import socket
from pigeon_constants import Pigeon_Constants as C
from Queue            import Queue
from upnp             import upnp
from pigeon_threads   import Pigeon_Threads


class Pigeon_Controller:
    def __init__(self, config, register, communicator, gui):
        # application objects
        self.config       = config
        self.register     = register
        self.communicator = communicator
        self.gui          = gui
        # controller objects
        self.msg_send = Queue()
        self.commands = Queue()
        self.local_ip = socket.gethostbyname(socket.gethostname()) # not 100% accurate
        self.upnp = upnp()
        # controller states
        self.ALIVE                = False
        self.IN_CONVERSATION      = False
        self.HANGUP               = False
        self.UPNP_PORTS_FORWARDED = False
        # controller commands
        self.command_map = {"/quit"      : self.do_quit,
                            "/rename"    : self.do_rename,
                            "/connect"   : self.do_connect,
                            "/hangup"    : self.do_hangup,
                            "/online"    : self.do_online,
                            "/register"  : self.do_register,
                            "/unregister": self.do_unregister,
                            "/commands"  : self.do_commands}

    # route a command to its associated function
    def handle_text(self, text):
        if len(text) > 1 and text[0] == "/":
            cmd_ary = text.replace("\n", "").split()
            if len(cmd_ary) > 1:
                cmd = cmd_ary[0]
                arg = cmd_ary[1]
            else:
                cmd = cmd_ary[0].replace(" ", "")
                arg = None
            try:
                self.command_map[cmd](arg)
            except KeyError:
                self.gui.sys_write("Invalid Command")
        elif self.IN_CONVERSATION:
            self.gui.chat_write(text, "You")
            self.msg_send.put(text)

    def name_sequence(self):
        self.ALIVE = True
        name = self.config.read_name()
        if not name:
            self.gui.sys_write("No name found! Try \"/rename [name]\"")
            name = C.DEFAULT_NAME
        return name

    def start(self):
        self.gui.start_gui(self)
        if not self.gui.HANDLES_MAIN_LOOP:
            self.start_writing()
        
    # call this to start the controller
    def start_writing(self):
        name = self.name_sequence()
        self.gui.sys_write("Forwarding router ports...")
        self.upnp_open_ports()
        self.gui.sys_write("Generating RSA keypair...")
        self.communicator.rsa_gen_keypair()
        self.gui.sys_write("Calling registration server...")
        if not self.register.register(name):
            self.gui.sys_write("Failed to register with " + self.register.server_ip)
        else:
            self.gui.sys_write("Registered with " + self.register.server_ip + " as " + name)
        # print online users 
        self.do_online(None)
        self.gui.sys_write("Welcome, " + name)
        self.gui.sys_write(C.START_MSG)

        # init wait_connection_background here
        self.conn_thread = threading.Thread(target=self.wait_connection_background) #stupid, needed?
        self.wait_conn_thread = threading.Thread(target=self.wait_connection_background)
        self.wait_conn_thread.start()

        if not self.gui.HANDLES_MAIN_LOOP:
            self.main_loop()

    # main input loop for controller
    def main_loop(self):
        while self.ALIVE:
            text = self.gui.get_text()
            if self.HANGUP:
                self.handle_hangup()
                continue
            self.handle_text(text)

    # command handler functions ~~~~

    def handle_hangup(self):
        self.HANGUP = False
        self.IN_CONVERSATION = False
        self.communicator.THREAD_STAY_ALIVE = False
        # join on any conversation thread
        if self.wait_conn_thread.isAlive():
            self.wait_conn_thread.join()
        elif self.conn_thread.isAlive():
            self.conn_thread.join()
        # start new wait_connection_background thread
        self.wait_conn_thread = threading.Thread(target=self.wait_connection_background)
        self.wait_conn_thread.start()
        self.gui.sys_write("Chat ended at " + time.ctime(time.time()))

    def do_commands(self, arg):
        self.gui.sys_write(C.COMMANDS)

    def do_online(self, arg):
        if self.register.CONNECTED:
            self.register.request_userlist(self.config.name)
            self.gui.print_userlist(self.register.userlist)

    def do_register(self, ip):
        #self.gui.sys_write("Type an IP address and hit [ENTER]")
        #ip = self.gui.get_text()
        # don't do anything if we are registered
        if not self.register.CONNECTED:
            self.register.set_server_ip(ip)
            self.gui.sys_write("Calling registration server...")
            if self.register.register(self.config.name):
                self.gui.sys_write("Registered with " + ip + " as " + self.config.name)
                self.do_online(None)
            else:
                self.gui.sys_write("Failed to register with server at " + ip)
        else:
            self.gui.sys_write("Already registered with a server!")

    def do_unregister(self, arg):
        if self.register.CONNECTED:
            self.register.unregister(self.config.name)
            self.gui.sys_write("Logged out of " + self.register.server_ip)
        else:
            self.gui.sys_write("Not registered with a server!")

    def do_rename(self, new_name):
        old_name = self.config.name
        if not self.config.change_name_config(new_name):
            self.gui.sys_write("Error changing name!")
            return
        if self.register.CONNECTED:
            self.register.re_register(old_name, new_name)
        self.gui.sys_write("Your new name is " + self.config.name)

    def do_quit(self, arg):
        self.gui.sys_write("Quitting...")
        self.msg_send.put(C.KILL)
        if self.register.CONNECTED:
            self.register.unregister(self.config.name)
        self.communicator.server_wait = False
        self.communicator.THREAD_STAY_ALIVE = False
        # join on conversation threads
        if self.wait_conn_thread.isAlive():
            self.wait_conn_thread.join()
        elif self.conn_thread.isAlive():
            self.conn_thread.join()
        self.upnp_close_ports()
        self.ALIVE = False
        self.gui.end_gui()

    def do_connect(self, other):
        # communicator needs to say this
        if not self.IN_CONVERSATION:
            # we want to spawn a thread here
            # to do connect_background
            self.communicator.server_wait = False  # stop comm.wait_connection
            self.wait_conn_thread.join()           # join wait thread
            self.conn_thread = threading.Thread(target=self.connect_background, args=(other,))
            self.conn_thread.start()

    def do_hangup(self, arg):
        if self.IN_CONVERSATION:
            self.msg_send.put(C.KILL)
            # TODO this might kill send threat too early?
            #self.communicator.THREAD_STAY_ALIVE = False
            self.HANGUP = True
            self.gui.chat_notify("You have disconnected, hit [ENTER] to leave")
        else:
            self.gui.sys_write("Not in a conversation!")

    # end command handler functions ~~~~

    # conversation threading functions ~~~
    
    def start_convo(self, conn, other_name):
        self.IN_CONVERSATION = True
        self.communicator.THREAD_STAY_ALIVE = True
        sender = threading.Thread(target=Pigeon_Threads.send_worker, args=(conn, self))
        sender.start()
        self.gui.chat_notify("Chat with " + other_name)
        Pigeon_Threads.receive_worker(conn, self, other_name)
        sender.join()
    
    def connect_background(self, ip):
        conn, other_name = self.communicator.attempt_connection(self.config.name, ip)
        if conn:
            self.start_convo(conn, other_name)
            conn.close()
        else:
            self.gui.sys_write("Failed to connect to " + ip)
            self.wait_conn_thread = threading.Thread(target=self.wait_connection_background)
            self.wait_conn_thread.start()

    def wait_connection_background(self):
        conn, other_name = self.communicator.wait_connection(self.config.name)
        if conn:
            self.start_convo(conn, other_name)
            conn.close()
            
    # end conversation threading functions ~~~

    # upnp helper functions ~~~

    def upnp_open_ports(self):
        if not self.upnp.establish_upnp_data():
            self.gui.sys_write("No router detected. UPnP disabled, or no router exists")
        else:
            self.UPNP_PORTS_FORWARDED = True
            res1 = self.upnp.udp_tunnel(C.CLIENT_TEST_PORT, self.local_ip)
            res2 = self.upnp.tcp_tunnel(C.CLIENT_MAIN_PORT, self.local_ip)
            res3 = self.upnp.udp_tunnel(C.CLIENT_REGISTER_PORT, self.local_ip)
            
            if int(res1.status) == 500:
                self.gui.sys_write("Failed to forward ports")
                self.UPNP_PORTS_FORWARDED = False

    def upnp_close_ports(self):
        if self.UPNP_PORTS_FORWARDED:
            res1 = self.upnp.udp_end_tunnel(C.CLIENT_TEST_PORT, self.local_ip)
            res2 = self.upnp.tcp_end_tunnel(C.CLIENT_MAIN_PORT, self.local_ip)
            res3 = self.upnp.udp_end_tunnel(C.CLIENT_REGISTER_PORT, self.local_ip)

            if int(res1.status) == 500:
                self.gui.sys_write("Failed to close ports")
            else:
                self.UPNP_PORTS_FORWARDED = False

    # end upnp helper functions ~~~
