"""
Pigeon is a peer-to-peer chat client with end-to-end encryption.
Copyright (C) 2016 Michael Wiktorek
"""

class Pigeon_Constants:
    # ports
    SERVER_MAIN_PORT = 5554  
    CLIENT_MAIN_PORT = 5555

    # messages
    ACK = "ack"
    REGISTER = "reg"
    UNREGISTER = "unreg"
    RE_REGISTER = "rereg"
    TEST = "test"
    REQUEST = "requ"
    KILL = "*>*>*>*>"
    RENAME = "<*<*<*<*"

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

    # commands ought to be made into constants
    CMD_LIST = ["/quit", "/connect", "/hangup",
                "/online", "/register", "/unregister",
                "/rename", "/commands"]
    
    CMD_LIST_ARGS = ["/connect", "/register", "/rename"]
