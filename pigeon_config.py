"""
Pigeon is a peer-to-peer chat client with end-to-end encryption.
Copyright (C) 2016 Michael Wiktorek
"""

from pigeon_constants import Pigeon_Constants as C

class Pigeon_Config:
    def __init__(self):
        self.name = C.DEFAULT_NAME

    def get_gui(self, gui):
        self.gui = gui
        self.display = gui.system_pad
        self.textbox = gui.textbox
        
    # attempt to read name from config file
    # if no file exists, create it
    def read_name(self):
        try:
            config_file = open("pigeon.conf", 'r')
            self.name = config_file.readline().replace("\n", "")
            config_file.close()
            return self.name
        except:
            return None

    # change our name in the configuration file
    def change_name_config(self, name):
        try:
            config_file = open("pigeon.conf", 'w')
            config_file.write(name + "\n")
            config_file.close()
            self.name = name
            return True
        except:
            return False
