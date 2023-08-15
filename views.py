import curses
from abc import ABC, abstractmethod
from services import EntryFileServices, InputService, PromptService


class Option:
    def __init__(self, display_name, action, color=None) -> None:
        self.display_name = display_name
        self.action = action
        self.color = color


class Menu(ABC):

    def __init__(self, stdscr) -> None:
        self.prompt_info = None
        self.stdscr = stdscr
        self.window = self._create_window()
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
                self.window.addstr(10 + idx, 10, f"> {option.display_name}", curses.A_BOLD | self.SELECTION_COLOR)
            else:
                self.window.addstr(10 + idx, 10, f"  {option.display_name}", color)
        if self.prompt_info:
            self.window.addstr(7, 7, self.prompt_info.get("msg"), self.prompt_info.get("color", self.RED))
        self.window.refresh()

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
        descriptions = EntryFileServices.get_all_entries_descriptions()
        if descriptions:
            options = [Option(desc, self.show_options) for desc in descriptions]
            options.append(Option("Go Back", self.exit_menu))
        else:
            desc = "There is nothing to show. Go back and add some entries!"
            options = [Option(desc, self.exit_menu)]
        self.options = options

    def show_options(self):
        PromptService.generate_prompt(self.stdscr)


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
