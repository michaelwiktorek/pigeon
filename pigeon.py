"""
Pigeon is a peer-to-peer chat client with end-to-end encryption.
Copyright (C) 2016 Michael Wiktorek

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
from pigeon_communicator   import Communicator
from pigeon_controller     import Pigeon_Controller
from pigeon_config         import Pigeon_Config
from pigeon_constants      import Pigeon_Constants as C
from pigeon_register_agent import Pigeon_Register_Agent
from curses_gui            import Curses_Gui
from tkinter_gui           import Tkinter_Gui
from rsa                   import RSA

# just import your gui and add it here!
gui_list = {"curses"  : Curses_Gui,
            "tkinter" : Tkinter_Gui}

def print_usage_exit():
    valid_guis = " | ".join(gui_list.keys())
    print "usage: python main.py < " + valid_guis + " >"
    sys.exit(0)

if __name__ == "__main__":

    #try:
    #    gui_choice = sys.argv[1].lower()
    #    gui = gui_list[gui_choice]()
    #except:
    #    print_usage_exit()
    gui = Tkinter_Gui()
    
    config = Pigeon_Config()
    register_agent = Pigeon_Register_Agent(sys.argv)
    communicator = Communicator(config, register_agent)
    controller = Pigeon_Controller(config, register_agent, communicator, gui)

    controller.start()
