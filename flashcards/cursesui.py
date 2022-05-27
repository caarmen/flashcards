"""
Curses-based console user interface
"""
import curses
import unicodedata
from curses.textpad import Textbox, rectangle

from flashcards.ui import Ui


class CursesUi(Ui):
    """
    Interact with the user in the flashcard game, in a console using curses
    """

    class _Windows:
        def __init__(self):
            # pylint: disable=no-member
            self.main = curses.newwin(curses.LINES, curses.COLS)
            self.guess_result = curses.newwin(1, 1)
            self.card = curses.newwin(1, 1)
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

    @classmethod
    def _get_text_coordinates(
        cls, offset_y_pct: float, text_length: int
    ) -> tuple[int, int]:
        # pylint doesn't realize that we'll have the LINES and COLS members
        # pylint: disable=no-member
        begin_y = int(curses.LINES * offset_y_pct)
        # pylint: disable=no-member
        begin_x = int((curses.COLS - text_length) / 2)
        return begin_y, begin_x

    @classmethod
    def _text_width(cls, text: str) -> int:
        wide_char_count = sum(
            [1 for ch in text if unicodedata.east_asian_width(ch) == "W"]
        )
        return wide_char_count + len(text)

    def _display_text(self, win, offset_y_pct: float, text: str):
        begin_y, begin_x = self._get_text_coordinates(
            offset_y_pct=offset_y_pct, text_length=self._text_width(text)
        )

        win.move(0, 0)
        win.bkgd(" ", curses.color_pair(1))
        win.clrtoeol()
        win.refresh()

        win.resize(1, self._text_width(text))
        win.mvwin(begin_y, begin_x)
        try:
            win.addstr(0, 0, text, curses.color_pair(1) | curses.A_BOLD)
        except curses.error:
            pass
        win.refresh()

    def _input_text(self, offset_y_pct: float, length: int) -> str:
        self._windows.input.clear()
        begin_y, begin_x = self._get_text_coordinates(
            offset_y_pct=offset_y_pct, text_length=length
        )

        self._windows.input_border.resize(3, length + 3)
        self._windows.input_border.mvwin(begin_y - 1, begin_x - 1)
        rectangle(self._windows.input_border, 0, 0, 2, length + 1)
        self._windows.input_border.refresh()

        self._windows.input.resize(1, length)
        self._windows.input.mvwin(begin_y, begin_x)
        self._windows.input.move(0, 0)
        text_box = Textbox(self._windows.input, insert_mode=True)
        return text_box.edit(validate=lambda x: x if x != 127 else curses.KEY_BACKSPACE).strip()

    def display_flashcard(self, index: int, total: int, flashcard: str):
        self._display_text(
            win=self._windows.card,
            offset_y_pct=0.33,
            text=self.translations("display_flashcard").format(
                index=index, total=total, key=flashcard
            ),
        )

    async def input_guess(self, flashcard: str) -> str:
        self._display_text(
            win=self._windows.input_label,
            offset_y_pct=0.5,
            text=self.translations("guess_prompt"),
        )
        return self._input_text(offset_y_pct=0.66, length=20)

    async def input_replay_missed_cards(self) -> bool:
        self._windows.input.clear()
        self._windows.input_border.clear()
        self._windows.input.refresh()
        self._windows.input_border.refresh()
        self._display_text(
            win=self._windows.input_label,
            offset_y_pct=0.5,
            text=self.translations("play_again"),
        )
        do_replay = (
            self._windows.input.getkey().casefold()
            == self.translations("answer_yes").casefold()
        )
        self._windows.score.clear()
        self._windows.score.refresh()
        return do_replay

    def display_right_guess(self, key: str, correct_answer: str):
        self._display_text(
            win=self._windows.guess_result,
            offset_y_pct=0.1,
            text=self.translations("right_guess"),
        )

    def display_wrong_guess(self, key: str, guess: str, correct_answer: str):
        self._display_text(
            win=self._windows.guess_result,
            offset_y_pct=0.1,
            text=self.translations("wrong_guess").format(correct_answer=correct_answer),
        )

    def display_score(self, correct_count: int, guessed_count: int):
        self._display_text(
            win=self._windows.score,
            offset_y_pct=0.8,
            text=self.translations("game_score").format(
                correct_count=correct_count, guessed_count=guessed_count
            ),
        )

    def game_over(self):
        self._windows.input.getch()
        curses.nocbreak()
        self._stdscr.keypad(False)
        curses.echo()
        curses.endwin()
