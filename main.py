import threading
import socket
import time
import curses
import curses.textpad

class ReceiverThread(threading.Thread):
    def run(self):
        return
        
class SenderThread(threading.Thread):
    def run(self):
        return

def display_message(message, pad, scroll):
    pad_y, pad_x = pad.getmaxyx()
    curs_y, curs_x = pad.getyx()
    pad.addstr("You:  " + message)
    pad.addstr(str(curs_y) + "/" + str(pad_y))
    
    if curs_y == pad_y - 1:
        scroll = scroll + 1
        pad.resize(pad_y+1, pad_x)

    pad.move(curs_y+1, 0)        
    pad.refresh(scroll,0, 0,0, pad_y, pad_x)
    return scroll


    
def main(screen):
    scr_y, scr_x = screen.getmaxyx()
    # we display chat history in the display_pad
    display_pad = curses.newpad(scr_y-1, scr_x)
    display_pad.idlok(1)
    display_pad.scrollok(True)
    scroll = 0
    # we display the message you type in the text window
    text_window = curses.newwin(1, scr_x, scr_y-1, 0)
    textbox = curses.textpad.Textbox(text_window, insert_mode=True)

    #loop accepting input and echoing to the display_pad
    while True:
        message = textbox.edit()
        # for whatever reason only the empty string matches correctly?
        if message == "":
            break
        text_window.clear()
        text_window.move(0,0)
        scroll = display_message(message, display_pad, scroll)
    
if __name__ == '__main__':
    curses.wrapper(main)
