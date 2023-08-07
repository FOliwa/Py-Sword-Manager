import curses
from services import EntryFileServices


def main(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)
    height, width = stdscr.getmaxyx()
    main_win = curses.newwin(height, width, 0, 0)
    MainView(main_win).run()


class MainView:

    def __init__(self, main_win) -> None:
        self.stdscr = curses.initscr()
        self.main_win = main_win
        self.options = ["Show saved entries", "Add new entry", "Exit"]
        self.selected_option = 0

    def display_window(self):
        for idx, option in enumerate(self.options):
            if idx == self.selected_option:
                self.main_win.addstr(10 + idx, 10, f"> {option}", curses.A_BOLD)
            else:
                self.main_win.addstr(10 + idx, 10, f"  {option}")
        self.main_win.refresh()

    def navigate(self):
        key = self.stdscr.getch()

        if key == curses.KEY_UP:
            self.selected_option = max(0, self.selected_option - 1)
        elif key == curses.KEY_DOWN:
            self.selected_option = min(len(self.options) - 1, self.selected_option + 1)
        elif key == ord('\n'):
            if self.selected_option == 0:
                # Show saved entries submenu
                pass
            elif self.selected_option == 1:
                # Handle Option 2
                pass
            elif self.selected_option == 2:
                return True

    def run(self):
        while True:
            self.main_win.clear()
            self.display_window()
            go_back = self.navigate()
            if go_back:
                break


curses.wrapper(main)
