class Pigeon_Constants:
    # ports
    SERVER_MAIN_PORT = 5554
    CLIENT_TEST_PORT = 5555
    CLIENT_MAIN_PORT = 1777

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
    DEFAULT_SERVER = "127.0.0.1"

    # names
    DEFAULT_NAME = "????"

    # keys
    ENTER = 10
    DEL = 127
    DEL_2 = 8
