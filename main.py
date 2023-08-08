import curses
from services import EntryFileServices


def setup_curses():
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
    stdscr = curses.initscr()
    height, width = stdscr.getmaxyx()
    main_win = curses.newwin(height, width, 0, 0)
    stdscr.keypad(True)
    return main_win, stdscr


def main(stdscr):
    main_win, stdscr = setup_curses()
    MainView(main_win, stdscr).run()


class MainView:

    def __init__(self, main_win, stdscr) -> None:
        self.prompt_info = None
        self.main_win = main_win
        self.stdscr = stdscr
        self.selected_option = 0
        self.options = [{"display_name": "Show Saved Entries",
                        "action": ListEntries(main_win, stdscr).run},
                        {"display_name": "Add New Entry",
                        "action": AddNewEntry(main_win, stdscr).run},
                        {"display_name": "Exit Program",
                        "action": lambda: True},
                        ]

    def display_window(self):
        for idx, option in enumerate(self.options):
            display_name = option.get('display_name', 'Error')
            color = option.get("color", curses.color_pair(1))
            if idx == self.selected_option:
                self.main_win.addstr(10 + idx, 10, f"> {display_name}", curses.A_BOLD | curses.color_pair(2))
            else:
                self.main_win.addstr(10 + idx, 10, f"  {display_name}", color)
        if self.prompt_info:
            self.main_win.addstr(7, 7, self.prompt_info, curses.color_pair(3))
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
        self._update_data()
        while True:
            self.main_win.clear()
            self.display_window()
            go_back = self.navigate()
            if go_back:
                break

    def _update_data(self):
        pass



class ListEntries(MainView):

    def __init__(self, main_win, stdscr) -> None:
        self.prompt_info = None
        self.main_win = main_win
        self.stdscr = stdscr
        self.selected_option = 0
        self.options = self.set_options()

    def set_options(self):
        descriptions = EntryFileServices.get_all_entries_descriptions()
        if descriptions:
            options = [{"display_name": desc, "action": None} for desc in descriptions]
            options.append({"display_name": "Go Back", "action": lambda: True})
            return options
        desc = "There is nothing to show. Go back and add some entries!"
        return [{"display_name": desc, "action": lambda: True}]

    def _update_data(self):
        self.options = self.set_options()


class AddNewEntry(MainView):

    def __init__(self, main_win, stdscr) -> None:
        self.main_win = main_win
        self.stdscr = stdscr
        self.selected_option = 0
        self.prompt_info = None

        self.description = None
        self.login = None
        self.password = None

        self.RED = curses.color_pair(3)
        self.GREEN = curses.color_pair(4)
        self.options = self.set_options()

    def set_options(self):
        options = [{"display_name": "Set entry description", "color": self.RED, "action": lambda: None},
                   {"display_name": "Set login", "color": self.RED, "action": lambda: None},
                   {"display_name": "Set password", "color": self.RED, "action": lambda: None},
                   {"display_name": "Save Entry", "action": self.save_entry},
                   {"display_name": "Go Back", "action": lambda: True}]
        return options

    def save_entry(self):
        if all([self.description, self.login, self.password]):
            result, msg = EntryFileServices.add_entry(self.description,
                                                      self.login,
                                                      self.password)
            self.prompt_info = msg
            return result
        self.prompt_info = "Provide missing data - marked on RED!"
        return False

    def _update_data(self):
        self._update_options_colors()
        self.selected_option = 0
        self.prompt_info = None

    def _update_options_colors(self):
        if self.description:
            self.options[0]["color"] = self.GREEN
        if self.login:
            self.options[1]["color"] = self.GREEN
        if self.password:
            self.options[2]["color"] = self.GREEN


curses.wrapper(main)
