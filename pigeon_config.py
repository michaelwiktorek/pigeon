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
    def obtain_name(self):
        name = C.DEFAULT_NAME
        try:
            config_file = open("pigeon.conf", 'r')
            name = config_file.readline().replace("\n", "")
            config_file.close()
        except:
            self.display.display_message("No name found!", "CONFIG")
            name = self.change_name_config()
        self.name = name
        return name

    # change our name in the configuration file
    def change_name_config(self):
        try:
            config_file = open("pigeon.conf", 'w')
            self.display.display_message("Type your new name and hit [ENTER]", "CONFIG")
            name = self.textbox.edit()
            config_file.write(name + "\n")
            config_file.close()
            self.display.display_message("Your name is now " + name, "CONFIG")
            self.name = name
            return name
        except:
            self.display.display_message("Error changing name!", "CONFIG")
