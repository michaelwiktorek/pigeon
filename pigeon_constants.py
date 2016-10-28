class Pigeon_Constants:
    # ports
    SERVER_MAIN_PORT     = 5554
    SERVER_REGISTER_PORT = 1812
    
    CLIENT_TEST_PORT     = 5555
    CLIENT_MAIN_PORT     = 1777
    CLIENT_REGISTER_PORT = 1791

    # messages
    ACK = "ack"
    REGISTER = "reg"
    UNREGISTER = "unreg"
    TEST = "test"
    REQUEST = "requ"
    KILL = "*>*>*>*>"

    # numbers
    ONLINE_TIMEOUT_SECS = 10  # set to 60 or higher for production use

    # addresses
    DEFAULT_SERVER = "www.michaelwiktorek.com"

    # names
    DEFAULT_NAME = "User"

    # keys
    ENTER = 10
    DEL = 127
    DEL_2 = 8

    # other stuff
    START_MSG = "Type /commands and hit [ENTER] for a list of commands!"
    COMMANDS = """Commands begin with a '/'.
Type a command and then hit [ENTER]
/quit            ... quit pigeon
/connect  [IP]   ... connect to another user
/hangup          ... end a conversation
/online          ... get a list of online users
/register [IP]   ... register with a server
/unregister      ... unregister with a server
/rename   [name] ... change your name
/commands        ... see a list of commands"""
