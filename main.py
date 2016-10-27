import sys
from pigeon_communicator import Communicator
from pigeon_controller import Pigeon_Controller
from pigeon_gui import Pigeon_GUI
from pigeon_threads import Pigeon_Threads
from pigeon_config import Pigeon_Config
from pigeon_constants import Pigeon_Constants as C
from pigeon_register_agent import Pigeon_Register_Agent
from curses_gui import Curses_Gui
from rsa import RSA

if __name__ == "__main__":
    # create communicator
    # create register agent
    # create GUI

    config = Pigeon_Config()

    register_agent = Pigeon_Register_Agent(sys.argv)

    communicator = Communicator(config, register_agent)

    gui = Curses_Gui()
    
    controller = Pigeon_Controller(config, register_agent, communicator, gui)

    controller.start()

    # GUI runs always
    #
    # communicator runs in background
    #   thread waiting for connection
    #   thread waiting on instructions:
    #     connect - pause conn thread, connect
    #     name - config.name_change
    #     quit - quit nicely
    #     r    - refresh userlist (?? auto)
    #   
    # register agent runs in background
    #   thread trying to connect to server
    #      writes to system window
    #   thread waiting on server REQUEST
    #      doesn't write
