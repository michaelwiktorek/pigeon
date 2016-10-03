class Pigeon_Config:
    def __init__(self):
        self.name = ""
    # attempt to read name from config file
    # if no file exists, create it
    def obtain_name(self):
        name = "Anonymous"
        try:
            config_file = open("pigeon.conf", 'r')
            print "Reading configuration file..."
            name = config_file.readline().replace("\n", "")
            config_file.close()
            print "Your name is " + name
        except:
            print "No configuration file found, creating..."
            config_file = open("pigeon.conf", 'w')
            name = raw_input("Enter your name: ")
            config_file.write(name + "\n")
            config_file.close()
            print "Your name is now " + name
        self.name = name
        return name

    # change our name in the configuration file
    def change_name_config(self, name):
        try:
            config_file = open("pigeon.conf", 'w')
            name = raw_input("Enter your name: ")
            config_file.write(name + "\n")
            config_file.close()
            print "Your name is now " + name
            self.name = name
        except:
            print "Error changing config file!"
