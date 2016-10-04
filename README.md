# pigeon

The absolutely awful chat program.

Pigeon is a cute little internet chat program written in Python 2.7. It is an extremely barebones project; you can wait on a connection from somebody else or you can try to connect directly to an IP address you know, in the hope that whoever is on the other side is also running a copy of pigeon, and is awaiting a connection.

If that sounds terrible to you, there's good news: Pigeon also comes with a cute little server that the chat client tries to connect to when you run it. It maintains a list of people who are connected and allows you to attempt to connect to other users by name.

Right now there are a few major flaws that make this program impractical:

1. You have to explicitly wait for a connection from another user. This should run in the background at all times.

2. The GUI is ugly, semi-functional, and extremely basic.

3. Pigeon does not yet support any kind of UPnP functionality, so if you're on a local network behind a router, then the program is only going to work under certain conditions, e.g. you're not connected to a Pigeon server and your client is acting as the "server" in the chat.

These flaws may be fixed at some point, but don't count on it. Feel free to write them for me.