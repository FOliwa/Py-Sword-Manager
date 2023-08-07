import curses

def main(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)

    height, width = stdscr.getmaxyx()
    main_win = curses.newwin(height, width, 0, 0)

    options = ["Option 1", "Option 2", "Exit"]
    selected_option = 0

    while True:
        main_win.clear()

        for idx, option in enumerate(options):
            if idx == selected_option:
                main_win.addstr(10 + idx, 10, f"> {option}", curses.A_BOLD)
            else:
                main_win.addstr(10 + idx, 10, f"  {option}")

        main_win.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected_option = max(0, selected_option - 1)
        elif key == curses.KEY_DOWN:
            selected_option = min(len(options) - 1, selected_option + 1)
        elif key == ord('\n'):
            if selected_option == 0:
                # Handle Option 1
                pass
            elif selected_option == 1:
                # Handle Option 2
                pass
            elif selected_option == 2:
                break

curses.wrapper(main)


# if __name__ == "__main__":
#     main()
