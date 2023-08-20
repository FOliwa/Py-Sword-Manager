import curses
from abc import ABC, abstractmethod
from functools import partial
from services import EntryFileServices, InputService, PromptService, AESService


class Option:
    def __init__(self, display_name, action, color=None) -> None:
        self.display_name = display_name
        self.action = action
        self.color = color


class Menu(ABC):

    BASE_WINDOW_X = 10
    BASE_WINDOW_Y = 10

    def __init__(self, stdscr, data=None) -> None:
        self.prompt_info = None
        self.stdscr = stdscr
        self.window = self._create_window()
        self.data = data
        self._set_colors()
        self._set_options()
        self._set_default_view_params()

    def _create_window(self):
        height, width = self.stdscr.getmaxyx()
        return curses.newwin(height, width, 0, 0)

    def _set_colors(self):
        self.WHITE = curses.color_pair(1)
        self.SELECTION_COLOR = curses.color_pair(2)
        self.RED = curses.color_pair(3)
        self.GREEN = curses.color_pair(4)

    @abstractmethod
    def _set_options(self):
        pass

    def exit_menu(self):
        return True

    def _set_default_view_params(self):
        self.prompt_info = None
        self.selected_option = 0

    def display_window(self):
        for idx, option in enumerate(self.options):
            color = option.color if option.color else self.WHITE
            if idx == self.selected_option:
                self.add_element(self.BASE_WINDOW_Y + idx, self.BASE_WINDOW_X, f"> {option.display_name}", curses.A_BOLD | self.SELECTION_COLOR)
            else:
                self.add_element(self.BASE_WINDOW_Y + idx, self.BASE_WINDOW_X, f"  {option.display_name}", color)
        if self.prompt_info:
            self.add_element(self.BASE_WINDOW_Y - 3, self.BASE_WINDOW_X, self.prompt_info.get("msg"), self.prompt_info.get("color", self.RED))
        self.window.refresh()

    def add_element(self, y, x, text, style):
        self.window.addstr(y, x, text, style)

    def navigate(self):
        key = self.stdscr.getch()
        if key == curses.KEY_UP:
            self.selected_option = max(0, self.selected_option - 1)
        elif key == curses.KEY_DOWN:
            self.selected_option = min(len(self.options) - 1, self.selected_option + 1)
        elif key == ord('\n'):
            action = self.options[self.selected_option].action
            return action() if action else None

    def run(self):
        while True:
            self.window.clear()
            self.display_window()
            go_back = self.navigate()
            if go_back:
                break
        curses.endwin()


class MainView(Menu):

    def _set_options(self):
        self.options = [
            Option("Show Saved Entries", self.show_saved_entries_view),
            Option("Add New Entry", self.add_new_entry_view),
            Option("Log Out", self.exit_menu),
        ]

    def show_saved_entries_view(self):
        action = ListEntriesView(self.stdscr)
        action.run()

    def add_new_entry_view(self):
        action = AddNewEntryView(self.stdscr)
        action.run()


class ListEntriesView(Menu):

    def _set_options(self):

        def show_entry_actions(data):
            action = EntryOptionsView(self.stdscr, data)
            action.refresh_list_view = self._set_options
            action.run()

        entries = EntryFileServices.get_all_entries()
        if entries:
            options = [Option(entry.get("description"), partial(show_entry_actions, entry.get("data"))) for entry in entries]
            options.append(Option("Go Back", self.exit_menu))
        else:
            desc = "There is nothing to show. Go back and add some entries!"
            options = [Option(desc, self.exit_menu)]
        self.options = options


class EntryOptionsView(Menu):

    BASE_WINDOW_X = 1
    BASE_WINDOW_Y = 1
    RELATED_LIST_VIEW = None

    def show_entry(self):
        data = AESService.decrypt(self.data)
        data = data.split(',')
        height, width = self.stdscr.getmaxyx()
        win_h, win_w = int(height/4), int(width/4)
        win_x, win_y = 30, 10
        PromptService.generate_prompt(win_x, win_y, win_h, win_w, msg=data)

    def _set_options(self):
        self.options = [
            Option("Show", self.show_entry),
            Option("Delete", self.delete_entry),
            Option("Return", self.exit_menu),
        ]

    def delete_entry(self):
        EntryFileServices.delete_entry(self.data)
        self.refresh_list_view()
        return True

    def _create_window(self):
        height, width = self.stdscr.getmaxyx()
        win_h, win_w = int(height/4), int(width/4)
        win_x, win_y = 30, 10
        input_window = curses.newwin(win_h, win_w, win_y, win_x)
        input_window.border()
        return input_window

    def display_window(self):
        self.window.border()
        return super().display_window()


class AddNewEntryView(Menu):

    def _set_default_view_params(self):
        self.selected_option = 0
        self.prompt_info = None
        self.description = None
        self.login = None
        self.password = None

    def _set_options(self):
        self.options = [
            Option("Set entry description     [ENTER]", self.set_description, self.RED),
            Option("Set login                 [ENTER]", self.set_login, self.RED),
            Option("Set password              [ENTER]", self.set_password, self.RED),
            Option("Save Entry", self.save_entry),
            Option("Go Back", self.exit_menu)
        ]

    def set_description(self):
        self.description = InputService.get_input_from_user(self.stdscr)
        self._update_options_colors()

    def set_login(self):
        self.login = InputService.get_input_from_user(self.stdscr)
        self._update_options_colors()

    def set_password(self):
        self.password = InputService.get_input_from_user(self.stdscr)
        self._update_options_colors()

    def save_entry(self):
        if all([self.description, self.login, self.password]):
            result, msg = EntryFileServices.add_entry(self.description,
                                                      self.login,
                                                      self.password)
            self.prompt_info = {"msg": msg}
            return result
        self.prompt_info = {"msg": "Provide missing data - marked on RED!"}
        return False

    def _update_options_colors(self):
        if self.description:
            self.options[0].color = self.GREEN
        if self.login:
            self.options[1].color = self.GREEN
        if self.password:
            self.options[2].color = self.GREEN
