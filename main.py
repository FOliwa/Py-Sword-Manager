import curses
from views import MainView
from services import LogInService


def setup_curses():
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
    stdscr = curses.initscr()
    stdscr.keypad(True)
    return stdscr


def main(stdscr):
    stdscr = setup_curses()
    if LogInService().authenticate_user(stdscr):
        MainView(stdscr).run()
    else:
        raise Exception("Wrong password")


curses.wrapper(main)
