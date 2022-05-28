"""
"Widget" implementations in ncurses
"""
import abc
import curses
from curses.textpad import rectangle
from typing import Callable

import unicodedata

from flashcards.cursesui.unicodetextbox import UnicodeTextbox
from flashcards.cursesui.safe_curses import safe_win_addstr, safe_curses_curs_set


def _text_width(text: str) -> int:
    wide_char_count = sum([1 for ch in text if unicodedata.east_asian_width(ch) == "W"])
    return wide_char_count + len(text)


class _BaseWindow:
    def __init__(self, parent_win, initial_lines: int = 1, initial_cols: int = 1):
        self._parent_win = parent_win
        self.win = curses.newwin(initial_lines, initial_cols)

    @abc.abstractmethod
    def redraw(self):
        """
        Redraw the widget
        """

    def hide(self):
        """
        Hide the widget
        """
        self.win.clear()
        self.win.bkgd(" ", curses.color_pair(1))
        self.win.refresh()


class BackgroundWindow(_BaseWindow):
    """
    Displays the background of the screen
    """

    def __init__(self, parent_win, color_pair):
        screen_lines, screen_cols = parent_win.getmaxyx()
        super().__init__(parent_win, screen_lines, screen_cols)
        self.win.bkgd(" ", color_pair)
        self.win.refresh()

    def redraw(self):
        screen_lines, screen_cols = self._parent_win.getmaxyx()
        self.win.resize(screen_lines, screen_cols)
        self.win.refresh()


class TextWindow(_BaseWindow):
    """
    Displays a text on the screen
    """

    def __init__(self, parent_win, offset_y: Callable[[int], int]):
        super().__init__(parent_win)
        self._offset_y = offset_y
        self._color_pair = curses.color_pair(1)
        self._color_attrs = curses.A_BOLD

    def set_text(self, text: str, color_pair: int = None, color_attrs: int = None):
        """
        Display a text
        :param text: the text to display
        :param color_pair: the color pair to use
        :param color_attrs: color attributes to use
        """
        screen_lines, screen_cols = self._parent_win.getmaxyx()
        begin_x = int((screen_cols - _text_width(text)) / 2)
        begin_y = self._offset_y(screen_lines)

        if color_pair:
            self._color_pair = color_pair
        if color_attrs:
            self._color_attrs = color_attrs

        self.win.move(0, 0)
        self.win.bkgd(" ", self._color_pair)
        self.win.clrtoeol()
        self.win.refresh()

        self.win.resize(1, max(_text_width(text), 1))
        self.win.mvwin(begin_y, begin_x)
        safe_win_addstr(self.win, 0, 0, text, self._color_pair | self._color_attrs)
        self.win.refresh()

    def redraw(self):
        text = self.win.instr(0, 0).decode("utf-8").strip()
        self.set_text(text)


class FlashcardBackground(_BaseWindow):
    """
    Displays the flashcard background
    """

    def __init__(self, parent_win):
        super().__init__(parent_win=parent_win)
        self.width = 0

    def redraw(self):
        screen_lines, screen_cols = self._parent_win.getmaxyx()
        self.win.erase()
        self.win.bkgd(" ", curses.color_pair(1))
        self.win.refresh()
        self.win.resize(5, self.width)
        self.win.bkgd(" ", curses.color_pair(1) | curses.A_REVERSE)
        self.win.mvwin(int(screen_lines / 2) - 5, int((screen_cols - self.width) / 2))
        self.win.box()
        self.win.refresh()


class InputBorder(_BaseWindow):
    """
    Displays a border around the input field
    """

    def __init__(self, parent_win):
        super().__init__(parent_win=parent_win)
        self.width = 0

    def redraw(self):
        screen_lines, screen_cols = self._parent_win.getmaxyx()
        begin_x = int((screen_cols - self.width) / 2)
        begin_y = int(screen_lines / 2) + 2
        self.win.bkgd(" ", curses.color_pair(1))
        self.win.erase()
        self.win.refresh()
        self.win.resize(3, self.width + 3)
        self.win.bkgd(" ", curses.color_pair(0))
        self.win.mvwin(begin_y - 1, begin_x - 1)
        rectangle(self.win, 0, 0, 2, self.width + 1)
        self.win.refresh()


class Input(_BaseWindow):
    """
    Displays the input field
    """

    def __init__(self, parent_win, callback: Callable[[int], None]):
        super().__init__(parent_win=parent_win)
        self._callback = callback
        self.width = 0

    def redraw(self, text: str = None):
        if text is None:
            text = self.win.instr(0, 0).decode("utf-8").strip()
        self.win.clear()
        screen_lines, screen_cols = self._parent_win.getmaxyx()
        begin_x = int((screen_cols - self.width) / 2)
        begin_y = int(screen_lines / 2) + 2

        self.win.move(0, 0)
        self.win.bkgd(" ", curses.color_pair(1))
        self.win.clrtoeol()
        self.win.refresh()

        self.win.resize(1, self.width)
        self.win.bkgd(" ", curses.color_pair(0))
        self.win.mvwin(begin_y, begin_x)
        self.win.move(0, 0)
        safe_win_addstr(self.win, 0, 0, text)
        safe_curses_curs_set(1)
        self.win.refresh()

    # Ignore invalid name for ch (we're reusing the existing name from the curses module)
    # pylint: disable=invalid-name
    def _input_validator(self, ch):
        if ch == 127:
            return curses.KEY_BACKSPACE
        if ch == curses.KEY_RESIZE:
            self._callback(ch)
        return ch

    def wait_for_string(self) -> str:
        text_box = UnicodeTextbox(self.win, length=self.width)
        return text_box.edit(validate=self._input_validator)

    def wait_for_key(self) -> str:
        """
        :return: the key input by the user
        """
        while True:
            # Ignore invalid name for ch (we're reusing the existing name from the curses module)
            # pylint: disable=invalid-name
            ch = self.win.getch()
            if ch > 0 and ch != curses.KEY_RESIZE:
                return chr(ch)
