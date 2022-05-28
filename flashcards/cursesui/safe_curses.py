import curses


def safe_curses_curs_set(visibility: int):
    try:
        curses.curs_set(visibility)
    except curses.error:
        pass


def safe_win_addstr(win, y: int, x: int, text: str, attr: int = None):
    try:
        if attr:
            win.addstr(y, x, text, attr)
        else:
            win.addstr(y, x, text)
    except curses.error:
        pass


def safe_win_addch(win, ch):
    try:
        win.addch(ch)
    except curses.error:
        pass
