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
        self.options = [{"display_name": "Show Saved Entries",
                        "action": ListView(main_win).run},
                        {"display_name": "Add New Entry",
                        "action": lambda: None},  
                        {"display_name": "Exit Program",
                        "action": lambda: True},
                        ]
        self.selected_option = 0

    def display_window(self):
        for idx, option in enumerate(self.options):
            display_name = option.get('display_name', 'Error')
            if idx == self.selected_option:
                self.main_win.addstr(10 + idx, 10, f"> {display_name}", curses.A_BOLD)
            else:
                self.main_win.addstr(10 + idx, 10, f"  {display_name}")
        self.main_win.refresh()

    def navigate(self):
        key = self.stdscr.getch()
        if key == curses.KEY_UP:
            self.selected_option = max(0, self.selected_option - 1)
        elif key == curses.KEY_DOWN:
            self.selected_option = min(len(self.options) - 1, self.selected_option + 1)
        elif key == ord('\n'):
            action = self.options[self.selected_option].get("action")
            return action() if action else None

    def run(self):
        while True:
            self.main_win.clear()
            self.display_window()
            go_back = self.navigate()
            if go_back:
                break


class ListView(MainView):

    def __init__(self, main_win) -> None:
        self.stdscr = curses.initscr()
        self.main_win = main_win
        self.options = self.set_options()
        self.selected_option = 0

    def set_options(self):
        descriptions = EntryFileServices.get_all_entries_descriptions()
        if descriptions:
            options = [{"display_name": desc, "action": None} for desc in descriptions]
            options.append({"display_name": "Go Back", "action": lambda: True})
            return options
        desc = "There is nothing to show. Go back and add some entries!"
        return [{"display_name": desc, "action": lambda: True}]


curses.wrapper(main)
