"""
Curses-based console user interface
"""
import curses
from curses.textpad import Textbox, rectangle

from flashcards.ui import Ui


class CursesUi(Ui):
    """
    Interface to interact with the user in the flashcard game, in a console using curses
    """

    def __init__(self, translations):
        self.translations = translations
        self._stdscr = curses.initscr()
        self._win_guess_result = curses.newwin(1, 1)
        self._win_card = curses.newwin(1, 1)
        self._win_input = curses.newwin(1, 1)
        self._win_input_label = curses.newwin(1, 1)
        self._win_input_border = curses.newwin(1, 1)
        curses.noecho()

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
    def _display_text(cls, win, offset_y_pct: float, text: str):
        begin_y, begin_x = cls._get_text_coordinates(
            offset_y_pct=offset_y_pct, text_length=len(text)
        )

        win.resize(1, 1)
        win.mvwin(begin_y, 1)
        # pylint: disable=no-member
        win.resize(1, curses.COLS)
        win.refresh()

        win.resize(1, len(text) + 5)
        win.mvwin(begin_y, begin_x)
        win.addstr(0, 0, text)

        win.refresh()

    def _input_text(self, offset_y_pct: float, length: int) -> str:
        self._win_input.clear()
        begin_y, begin_x = self._get_text_coordinates(
            offset_y_pct=offset_y_pct, text_length=length
        )

        self._win_input_border.resize(3, length + 3)
        self._win_input_border.mvwin(begin_y - 1, begin_x - 1)
        rectangle(self._win_input_border, 0, 0, 2, length + 1)
        self._win_input_border.refresh()

        self._win_input.resize(1, length)
        self._win_input.mvwin(begin_y, begin_x)
        self._win_input.move(0, 0)
        text_box = Textbox(self._win_input, insert_mode=True)
        text_box.edit(validate=lambda x: x if x != 127 else curses.KEY_BACKSPACE)
        self._win_input.refresh()
        return text_box.gather().strip()

    def display_flashcard(self, index: int, total: int, flashcard: str):
        self._display_text(
            win=self._win_card,
            offset_y_pct=0.33,
            text=self.translations("display_flashcard").format(
                index=index, total=total, key=flashcard
            ),
        )

    async def input_guess(self, flashcard: str) -> str:
        self._display_text(
            win=self._win_input_label,
            offset_y_pct=0.5,
            text=self.translations("guess_prompt"),
        )
        return self._input_text(offset_y_pct=0.66, length=20)

    async def input_replay_missed_cards(self) -> bool:
        self._display_text(
            win=self._win_input_label,
            offset_y_pct=0.5,
            text=self.translations("play_again"),
        )
        return (
            self._input_text(offset_y_pct=0.66, length=20).casefold()
            == self.translations("answer_yes").casefold()
        )

    def display_right_guess(self, key: str, correct_answer: str):
        self._display_text(
            win=self._win_guess_result,
            offset_y_pct=0.1,
            text=self.translations("right_guess"),
        )

    def display_wrong_guess(self, key: str, guess: str, correct_answer: str):
        self._display_text(
            win=self._win_guess_result,
            offset_y_pct=0.1,
            text=self.translations("wrong_guess").format(correct_answer=correct_answer),
        )

    def display_score(self, correct_count: int, guessed_count: int):
        self._display_text(
            win=self._win_card,
            offset_y_pct=0.8,
            text=self.translations("game_score").format(
                correct_count=correct_count, guessed_count=guessed_count
            ),
        )
