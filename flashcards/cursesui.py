"""
Curses-based console user interface
"""
import curses
from typing import Callable

import unicodedata
from curses.textpad import Textbox, rectangle
from curses.ascii import isprint, iscntrl

from flashcards.ui import Ui


class UnicodeTextbox(Textbox):
    """
    Add some support for unicode to Textbox
    """

    def __init__(self, win, length):
        super().__init__(win)
        self.length = length
        self.win = win

    def do_command(self, ch):
        if ch < 0 or isprint(ch) or iscntrl(ch) or curses.KEY_MIN < ch < curses.KEY_MAX:
            return super().do_command(ch)
        try:
            self.win.addch(ch)
        except curses.error:
            pass
        return 1

    def gather(self) -> str:
        return self.win.instr(0, 0).decode("utf-8")


def _get_text_coordinates(screen_lines: int, screen_cols: int, offset_y: int, text_length: int) -> tuple[int, int]:
    begin_y = int(screen_lines / 2) + offset_y
    begin_x = int((screen_cols - text_length) / 2)
    return begin_y, begin_x


def _text_width(text: str) -> int:
    wide_char_count = sum(
        [1 for ch in text if unicodedata.east_asian_width(ch) == "W"]
    )
    return wide_char_count + len(text)


class _TextWindow:
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


class _FlashcardBackground(_TextWindow):

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


class _InputBorder(_TextWindow):
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


class _Input(_TextWindow):
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


class CursesUi(Ui):
    """
    Interact with the user in the flashcard game, in a console using curses
    """

    # pylint: disable=too-few-public-methods,too-many-instance-attributes
    class _Windows:
        def __init__(self, root_window):
            # pylint: disable=no-member
            self.main = curses.newwin(curses.LINES, curses.COLS)
            self.guess_result = _TextWindow(parent_win=root_window, offset_y=lambda lines, cols: int(lines / 2) - 8)
            self.progress = _TextWindow(parent_win=root_window, offset_y=lambda lines, cols: lines - 1)
            self.card_bkgd = _FlashcardBackground(parent_win=root_window)
            self.card_text = _TextWindow(parent_win=root_window, offset_y=lambda lines, cols: int(lines / 2) - 3)
            self.input_label = _TextWindow(parent_win=root_window, offset_y=lambda lines, cols: int(lines / 2) + 3)
            self.input = _Input(parent_win=root_window)
            self.input_border = _InputBorder(parent_win=root_window)
            self.score = _TextWindow(parent_win=root_window, offset_y=lambda lines, cols: int(lines / 2) + 6)
            self.text_windows = [
                self.guess_result,
                self.progress,
                self.input_label,
                self.input_border,
                self.input,
                self.score,
                self.card_bkgd,
                self.card_text,
            ]

    def __init__(self, translations):
        self.translations = translations
        self._stdscr = curses.initscr()
        curses.noecho()
        curses.start_color()
        if curses.has_colors():
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
            curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
        self._windows = self._Windows(self._stdscr)
        self._windows.main.bkgd(" ", curses.color_pair(1))
        self._windows.main.refresh()

    @property
    def _lines(self) -> int:
        # pylint doesn't realize that we'll have the LINES and COLS members
        # pylint: disable=no-member
        return self._stdscr.getmaxyx()[0]

    @property
    def _cols(self) -> int:
        # pylint: disable=no-member
        return self._stdscr.getmaxyx()[1]

    def _display_input_box(self, offset_y: int, length: int):
        self._windows.input_border.width = length
        self._windows.input_border.set_text("")
        self._windows.input.width = length
        self._windows.input.set_text("")

    def _horse(self, ch):
        if ch == 127:
            return curses.KEY_BACKSPACE
        if ch == curses.KEY_RESIZE:
            for win in self._windows.text_windows:
                win.redraw()
        return ch

    def _input_text(self, offset_y: int, length: int) -> str:
        self._display_input_box(offset_y=offset_y, length=length)
        text_box = UnicodeTextbox(self._windows.input.win, length=length)
        return text_box.edit(validate=self._horse)

    def display_flashcard(
            self, index: int, total: int, flashcard: str, max_key_length: int
    ):
        self._windows.progress.set_text(
            text=self.translations("progress").format(index=index, total=total),
            color_attrs=curses.A_DIM,
        )
        flashcard_width = max_key_length + 8
        if flashcard_width % 2 != 0:
            flashcard_width += 1

        self._windows.card_bkgd.width = flashcard_width
        self._windows.card_bkgd.set_text("")
        self._windows.card_text.set_text(
            text=self.translations("display_flashcard").format(key=flashcard),
            color_pair=curses.color_pair(2),
        )

    async def input_guess(self, flashcard: str, max_answer_length: int) -> str:
        input_width = max_answer_length + 1
        if input_width % 2 != 0:
            input_width += 1
        return self._input_text(offset_y=3, length=input_width)

    async def input_replay_missed_cards(self) -> bool:
        self._windows.input_label.set_text(
            text=self.translations("play_again"),
            color_attrs=curses.A_BLINK,
        )
        self._windows.input.hide()
        self._windows.input_border.hide()
        self._windows.input_label.win.move(0, 0)
        self._windows.input_label.redraw()
        try:
            curses.curs_set(0)
        except curses.error:
            pass
        key = self._windows.input.wait_for_key()
        do_replay = (key.casefold() == self.translations("answer_yes").casefold())
        try:
            curses.curs_set(1)
        except curses.error:
            pass
        self._windows.score.hide()
        self._windows.input_label.hide()
        self._windows.guess_result.hide()
        return do_replay

    def display_right_guess(self, key: str, correct_answer: str):
        self._windows.guess_result.set_text(
            text=self.translations("right_guess"),
        )

    def display_wrong_guess(self, key: str, guess: str, correct_answer: str):
        self._windows.guess_result.set_text(
            text=self.translations("wrong_guess").format(correct_answer=correct_answer),
        )

    def display_score(self, correct_count: int, guessed_count: int):
        self._windows.score.set_text(
            text=self.translations("game_score").format(
                correct_count=correct_count, guessed_count=guessed_count
            ),
            color_attrs=curses.A_UNDERLINE,
        )

    def game_over(self):
        try:
            curses.curs_set(0)
        except curses.error:
            pass
        self._windows.input.wait_for_key()
        try:
            curses.curs_set(1)
        except curses.error:
            pass
        curses.nocbreak()
        self._stdscr.keypad(False)
        curses.echo()
        curses.endwin()
