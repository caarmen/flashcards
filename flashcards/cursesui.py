"""
Curses-based console user interface
"""
import curses
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


class CursesUi(Ui):
    """
    Interact with the user in the flashcard game, in a console using curses
    """

    # pylint: disable=too-few-public-methods,too-many-instance-attributes
    class _Windows:
        def __init__(self):
            # pylint: disable=no-member
            self.main = curses.newwin(curses.LINES, curses.COLS)
            self.guess_result = curses.newwin(1, 1)
            self.progress = curses.newwin(1, 1)
            self.card_bkgd = curses.newwin(1, 1)
            self.card_text = curses.newwin(1, 1)
            self.input_label = curses.newwin(1, 1)
            self.input = curses.newwin(1, 1)
            self.input_border = curses.newwin(1, 1)
            self.score = curses.newwin(1, 1)

    def __init__(self, translations):
        self.translations = translations
        self._stdscr = curses.initscr()
        curses.noecho()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        self._windows = self._Windows()
        self._windows.main.bkgd(" ", curses.color_pair(1))
        self._windows.main.refresh()

    @property
    def _lines(self) -> int:
        # pylint doesn't realize that we'll have the LINES and COLS members
        # pylint: disable=no-member
        return curses.LINES

    @property
    def _cols(self) -> int:
        # pylint: disable=no-member
        return curses.COLS

    def _get_text_coordinates(self, offset_y: int, text_length: int) -> tuple[int, int]:
        begin_y = int(self._lines / 2) + offset_y
        begin_x = int((self._cols - text_length) / 2)
        return begin_y, begin_x

    @classmethod
    def _text_width(cls, text: str) -> int:
        wide_char_count = sum(
            [1 for ch in text if unicodedata.east_asian_width(ch) == "W"]
        )
        return wide_char_count + len(text)

    def _display_text(self, win, offset_y: int, text: str, color_pair=None):
        begin_y, begin_x = self._get_text_coordinates(
            offset_y=offset_y, text_length=self._text_width(text)
        )

        if not color_pair:
            color_pair = curses.color_pair(1)

        win.move(0, 0)
        win.bkgd(" ", color_pair)
        win.clrtoeol()
        win.refresh()

        win.resize(1, self._text_width(text))
        win.mvwin(begin_y, begin_x)
        try:
            win.addstr(0, 0, text, curses.A_BOLD)
        except curses.error:
            pass
        win.refresh()

    def _display_input_box(self, offset_y: int, length: int):
        self._windows.input.clear()
        begin_y, begin_x = self._get_text_coordinates(
            offset_y=offset_y, text_length=length
        )

        self._windows.input_border.resize(3, length + 3)
        self._windows.input_border.mvwin(begin_y - 1, begin_x - 1)
        rectangle(self._windows.input_border, 0, 0, 2, length + 1)
        self._windows.input_border.refresh()

        self._windows.input.resize(1, length)
        self._windows.input.mvwin(begin_y, begin_x)
        self._windows.input.move(0, 0)

    def _input_text(self, offset_y: int, length: int) -> str:
        self._display_input_box(offset_y=offset_y, length=length)
        text_box = UnicodeTextbox(self._windows.input, length=length)
        return text_box.edit(validate=lambda x: x if x != 127 else curses.KEY_BACKSPACE)

    def display_flashcard(
        self, index: int, total: int, flashcard: str, max_key_length: int
    ):
        self._display_text(
            win=self._windows.progress,
            offset_y=7,
            text=self.translations("progress").format(index=index, total=total),
        )
        flashcard_width = max_key_length + 8
        self._windows.card_bkgd.erase()
        self._windows.card_bkgd.bkgd(" ", curses.color_pair(1))
        self._windows.card_bkgd.refresh()
        self._windows.card_bkgd.resize(5, flashcard_width)
        self._windows.card_bkgd.bkgd(" ", curses.color_pair(1) | curses.A_REVERSE)
        self._windows.card_bkgd.mvwin(
            int(self._lines / 2) - 5, int((self._cols - flashcard_width) / 2)
        )
        self._windows.card_bkgd.box()
        self._windows.card_bkgd.refresh()
        self._display_text(
            win=self._windows.card_text,
            offset_y=-3,
            text=self.translations("display_flashcard").format(key=flashcard),
            color_pair=curses.color_pair(1) | curses.A_REVERSE,
        )

    async def input_guess(self, flashcard: str, max_answer_length: int) -> str:
        self._display_text(
            win=self._windows.input_label,
            offset_y=3,
            text=self.translations("guess_prompt"),
        )
        return self._input_text(offset_y=3, length=max_answer_length + 1)

    async def input_replay_missed_cards(self) -> bool:
        self._display_text(
            win=self._windows.input_label,
            offset_y=1,
            text=self.translations("play_again"),
        )
        self._windows.input.clear()
        self._windows.input_border.clear()
        self._windows.input.refresh()
        self._windows.input_border.refresh()
        self._windows.input_label.move(0, 0)
        curses.curs_set(0)
        do_replay = (
            self._windows.input.getkey().casefold()
            == self.translations("answer_yes").casefold()
        )
        curses.curs_set(1)
        self._windows.score.clear()
        self._windows.score.refresh()
        return do_replay

    def display_right_guess(self, key: str, correct_answer: str):
        self._display_text(
            win=self._windows.guess_result,
            offset_y=-8,
            text=self.translations("right_guess"),
        )

    def display_wrong_guess(self, key: str, guess: str, correct_answer: str):
        self._display_text(
            win=self._windows.guess_result,
            offset_y=-8,
            text=self.translations("wrong_guess").format(correct_answer=correct_answer),
        )

    def display_score(self, correct_count: int, guessed_count: int):
        self._display_text(
            win=self._windows.score,
            offset_y=7,
            text=self.translations("game_score").format(
                correct_count=correct_count, guessed_count=guessed_count
            ),
        )

    def game_over(self):
        curses.curs_set(0)
        self._windows.input.getch()
        curses.curs_set(1)
        curses.nocbreak()
        self._stdscr.keypad(False)
        curses.echo()
        curses.endwin()
