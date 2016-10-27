import curses
from pigeon_constants import Pigeon_Constants as C

# This class keeps the GUI code isolated from the controller code
class Curses_Gui:
    def __init__(self):
        return

    def start_gui(self):
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.screen.keypad(1)
        self.initialize_elements()

    def end_gui(self):
        curses.nocbreak()
        self.screen.keypad(0)
        curses.echo()
        curses.endwin()

    def initialize_elements(self):
        scr_y, scr_x = self.screen.getmaxyx()

        # four different windows for displaying text
        self.chat_pad     = Scroll_Pad(2*scr_y/3, 2*scr_x/3, 0, 0)
        self.system_pad   = Scroll_Pad(2*scr_y/3, 2*scr_x/3, 0, 0)
        self.textbox      = Simple_Textbox(3, scr_x, scr_y-3, 0, self)
        self.userlist_pad = Scroll_Pad(2*scr_y/3, scr_x/3, 0, 2*scr_x/3)

    def sys_write(self, message):
        self.system_pad.write_from_name(message, "SYSTEM")

    def chat_write(self, message, name):
        self.chat_pad.write_from_name(message, name)

    def chat_notify(self, message):
        self.chat_pad.write_from_name(message, "SYSTEM")

    def print_userlist(self, userlist):
        for addr in userlist.keys():
            self.userlist_pad.write(userlist[addr][0] + " at " + addr)

    def get_text(self):
        return self.textbox.edit()

    def resize_handler(self):
        scr_y, scr_x = self.screen.getmaxyx()
        self.screen.clear()
        self.screen.refresh()
        self.chat_pad.resize(2*scr_y/3, 2*scr_x/3)
        self.system_pad.resize(2*scr_y/3, 2*scr_x/3)
        self.userlist_pad.resize(2*scr_y/3, scr_x/3-1)
        self.userlist_pad.move(0, 2*scr_x/3)
        self.textbox.move(scr_y-3, 0)
        self.textbox.resize(3, scr_x)
        self.chat_pad.refresh()
        self.system_pad.refresh()
        self.userlist_pad.refresh()
        curses.resizeterm(scr_y, scr_x)



# extension of curses pad that scrolls
class Scroll_Pad:
    def __init__(self, nrow, ncol, y, x):
        self.display = curses.newpad(nrow, ncol)
        self.scroll = 0
        self.init_ncol = ncol
        self.y = y
        self.x = x
        self.nrow = nrow
        self.ncol = ncol
        self.display.border()
        self.display.idlok(1)
        self.display.scrollok(True)
        self.display.leaveok(0)
        self.refresh()
        
    def refresh(self):
        self.display.refresh(self.scroll, 0, self.y, self.x, self.nrow + self.y, self.ncol + self.x)

    def resize(self, nrow, ncol):
        curs_y, curs_x = self.display.getyx()
        if curs_y < nrow - 1:
            self.display.resize(nrow, self.init_ncol)
        else:
            self.scroll = (curs_y - nrow)
        self.nrow = nrow
        self.ncol = ncol

    def move(self, y, x):
        self.y = y
        self.x = x

    def write(self, message):
        self.display.addstr(message)
        self.display.addch('\n')
        self.refresh()

    def write_from_name(self, message, name):
        self.write(name + ": " + message)

# collects text, including resize character
class Simple_Textbox:
    def __init__(self, nrow, ncol, y, x, gui):
        self.gui = gui # ugly hack
        self.y = y
        self.x = x
        self.nrow = nrow
        self.ncol = ncol
        self.win = curses.newwin(nrow, ncol, y, x)
        self.str = []

    def move(self, y, x):
        self.win.mvwin(y, x)
        self.y = y
        self.x = x
        
    def resize(self, nrow, ncol):
        self.win.resize(nrow, ncol)
        self.nrow = nrow
        self.ncol = ncol

    # let's just say that this needs some work
    def edit(self):
        while True:
            ch = self.win.getch()
            if ch == curses.KEY_RESIZE:         # RESIZE
                self.gui.resize_handler()
                continue
            elif ch == C.ENTER:                 # ENTER
                self.win.clear()
                self.win.move(0,0)
                self.win.refresh()
                output = "".join(self.str)
                self.str = []
                return output
            elif ch == C.DEL or ch == C.DEL_2:  # DELETE
                curs_y, curs_x = self.win.getyx()
                win_y, win_x = self.win.getmaxyx()
                # garbage move cursor
                if curs_x > 0:
                    self.str.pop()
                    self.win.move(curs_y, curs_x-1)
                elif curs_y >= 1:
                    self.str.pop()
                    self.win.move(curs_y-1, win_x-1)
                    
                self.win.delch()
            else:                               # OTHER CHARACTER
                curs_y, curs_x = self.win.getyx()
                win_y, win_x = self.win.getmaxyx()
                if curs_x == win_x-1:
                    if curs_y < win_y-1:
                        self.win.addch(chr(ch))
                        self.str.append(chr(ch))
                        self.win.move(curs_y + 1, 0)
                else:
                    self.win.addch(chr(ch))
                    self.str.append(chr(ch))
                    self.win.move(curs_y, curs_x + 1)
                self.win.refresh()


