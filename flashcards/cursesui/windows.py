import curses
from curses.textpad import rectangle
from typing import Callable

import unicodedata


def _text_width(text: str) -> int:
    wide_char_count = sum(
        [1 for ch in text if unicodedata.east_asian_width(ch) == "W"]
    )
    return wide_char_count + len(text)


class BackgroundWindow:
    def __init__(self, parent_win, color_pair):
        self._parent_win = parent_win
        screen_lines, screen_cols = self._parent_win.getmaxyx()
        self.win = curses.newwin(screen_lines, screen_cols)
        self.win.bkgd(" ", color_pair)
        self.win.refresh()

    def redraw(self):
        screen_lines, screen_cols = self._parent_win.getmaxyx()
        self.win.resize(screen_lines, screen_cols)
        self.win.refresh()


class TextWindow:
    def __init__(self, parent_win, offset_y: Callable[[int, int], int]):
        self._parent_win = parent_win
        self.win = curses.newwin(1, 1)
        self._offset_y = offset_y
        self._color_pair = curses.color_pair(1)
        self._color_attrs = curses.A_BOLD

    def set_text(self, text: str, color_pair: int = None, color_attrs: int = curses.A_BOLD):
        screen_lines, screen_cols = self._parent_win.getmaxyx()
        begin_x = int((screen_cols - _text_width(text)) / 2)
        begin_y = self._offset_y(screen_lines, screen_cols)

        if color_pair:
            self._color_pair = color_pair
        self._color_attrs = color_attrs

        self.win.move(0, 0)
        self.win.bkgd(" ", self._color_pair)
        self.win.clrtoeol()
        self.win.refresh()

        self.win.resize(1, max(_text_width(text), 1))
        self.win.mvwin(begin_y, begin_x)
        try:
            self.win.addstr(0, 0, text, self._color_pair | self._color_attrs)
        except curses.error:
            pass
        self.win.refresh()

    def redraw(self):
        text = self.win.instr(0, 0).decode("utf-8").strip()
        self.set_text(text, color_pair=self._color_pair, color_attrs=self._color_attrs)

    def hide(self):
        self.win.clear()
        self.win.bkgd(" ", curses.color_pair(1))
        self.win.refresh()

    def wait_for_key(self) -> str:
        while True:
            ch = self.win.getch()
            if ch > 0 and ch != curses.KEY_RESIZE:
                return chr(ch)


class FlashcardBackground(TextWindow):

    def __init__(self, parent_win):
        super().__init__(parent_win=parent_win, offset_y=lambda lines, cols: int(lines / 2) - 5)
        self.width = 0

    def set_text(self, text: str, color_pair: int = None, color_attrs: int = curses.A_BOLD):
        screen_lines, screen_cols = self._parent_win.getmaxyx()
        self.win.erase()
        self.win.bkgd(" ", curses.color_pair(1))
        self.win.refresh()
        self.win.resize(5, self.width)
        self.win.bkgd(" ", curses.color_pair(1) | curses.A_REVERSE)
        self.win.mvwin(
            int(screen_lines / 2) - 5, int((screen_cols - self.width) / 2)
        )
        self.win.box()
        self.win.refresh()


class InputBorder(TextWindow):
    def __init__(self, parent_win):
        super().__init__(parent_win=parent_win, offset_y=lambda lines, cols: int(lines / 2) + 2)
        self.width = 0

    def set_text(self, text: str, color_pair: int = None, color_attrs: int = curses.A_BOLD):
        screen_lines, screen_cols = self._parent_win.getmaxyx()
        begin_x = int((screen_cols - self.width) / 2)
        begin_y = self._offset_y(screen_lines, screen_cols)
        self.win.bkgd(" ", curses.color_pair(1))
        self.win.erase()
        self.win.refresh()
        self.win.resize(3, self.width + 3)
        self.win.bkgd(" ", curses.color_pair(0))
        self.win.mvwin(begin_y - 1, begin_x - 1)
        rectangle(self.win, 0, 0, 2, self.width + 1)
        self.win.refresh()


class Input(TextWindow):
    def __init__(self, parent_win):
        super().__init__(parent_win=parent_win, offset_y=lambda lines, cols: int(lines / 2) + 2)
        self.width = 0

    def set_text(self, text: str, color_pair: int = None, color_attrs: int = curses.A_BOLD):
        self.win.clear()
        screen_lines, screen_cols = self._parent_win.getmaxyx()
        begin_x = int((screen_cols - self.width) / 2)
        begin_y = self._offset_y(screen_lines, screen_cols)

        self.win.move(0, 0)
        self.win.bkgd(" ", curses.color_pair(1))
        self.win.clrtoeol()
        self.win.refresh()

        self.win.resize(1, self.width)
        self.win.bkgd(" ", curses.color_pair(0))
        self.win.mvwin(begin_y, begin_x)
        self.win.move(0, 0)
        try:
            self.win.addstr(0, 0, text)
        except curses.error:
            pass
        self.win.refresh()
