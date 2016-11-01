# pigeon

The absolutely awful chat program.

Pigeon is a cute little chat program written in Python 2.7. It comes packaged with a simple registration server that track and communicate a list of online users, but its messaging system operates on a strictly peer-to-peer basis and does not need the server to operate.

To run the program, type "python main.py", with arguments "tkinter" or "curses" depending on which GUI you wish to use. "tkinter" is recommended. If no argument is passed, pigeon will start with the tkinter GUI.

To run the server, type "python server.py".

Pigeon generates an RSA keypair when it starts up and uses this to encrypt messages. However, it is probably not cryptographically secure. At this moment Pigeon does not support chatting with multiple other users at once. 
