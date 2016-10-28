import sys
from pigeon_communicator   import Communicator
from pigeon_controller     import Pigeon_Controller
from pigeon_config         import Pigeon_Config
from pigeon_constants      import Pigeon_Constants as C
from pigeon_register_agent import Pigeon_Register_Agent
from curses_gui            import Curses_Gui
from tkinter_gui           import Tkinter_Gui
from rsa                   import RSA

if __name__ == "__main__":
    
    config = Pigeon_Config()

    register_agent = Pigeon_Register_Agent(sys.argv)

    communicator = Communicator(config, register_agent)

    #gui = Curses_Gui()
    gui = Tkinter_Gui()
    
    controller = Pigeon_Controller(config, register_agent, communicator, gui)

    controller.start()
