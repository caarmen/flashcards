"""
Exception catching wrappers around curses apis
"""
import curses


def safe_curses_curs_set(visibility: int):
    """
    Safely call curses.curs_set
    """
    try:
        curses.curs_set(visibility)
    except curses.error:
        pass


# x and y are perfrectly fine
# pylint: disable=invalid-name
def safe_win_addstr(win, y: int, x: int, text: str, attr: int = None):
    """
    Safely call win.addstr
    """
    try:
        if attr:
            win.addstr(y, x, text, attr)
        else:
            win.addstr(y, x, text)
    except curses.error:
        pass


# Ignore invalid name for ch (we're reusing the existing name from the curses module)
# pylint: disable=invalid-name
def safe_win_addch(win, ch):
    """
    Safely call win.addch
    """
    try:
        win.addch(ch)
    except curses.error:
        pass
