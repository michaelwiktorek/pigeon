from pigeon_constants import Pigeon_Constants as C

class Pigeon_Config:
    def __init__(self, gui):
        self.name = C.DEFAULT_NAME
        self.gui = gui
    # attempt to read name from config file
    # if no file exists, create it
    def obtain_name(self):
        name = C.DEFAULT_NAME
        try:
            config_file = open("pigeon.conf", 'r')
            name = config_file.readline().replace("\n", "")
            config_file.close()
        except:
            config_file = open("pigeon.conf", 'w')
            #name = raw_input("Enter your name: ")
            config_file.write(name + "\n")
            config_file.close()
        self.name = name
        return name

    # change our name in the configuration file
    def change_name_config(self, name):
        try:
            config_file = open("pigeon.conf", 'w')
            #name = raw_input("Enter your name: ")
            config_file.write(name + "\n")
            config_file.close()
            self.name = name
        except:
            print "we should write error to sys_display"
