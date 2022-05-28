"""
Curses-based console user interface
"""
import curses
from typing import Callable

from flashcards.cursesui.safe_curses import safe_curses_curs_set
from flashcards.cursesui.windows import (
    Background,
    Label,
    Card,
    Input,
    InputBorder,
    StatusBar,
)
from flashcards.ui import Ui


class CursesUi(Ui):
    """
    Interact with the user in the flashcard game, in a console using curses
    """

    # pylint: disable=too-few-public-methods,too-many-instance-attributes
    class _Windows:
        def __init__(self, root_window, key_input_callback: Callable[[int], None]):
            # pylint: disable=no-member
            self.main = Background(root_window, color_pair=curses.color_pair(1))
            self.guess_result = Label(
                parent_win=root_window, offset_y=lambda lines: lines // 2 - 8
            )
            self.statusbar = StatusBar(
                parent_win=root_window, color_pair=curses.color_pair(3)
            )
            self.card_bkgd = Card(parent_win=root_window)
            self.card_text = Label(
                parent_win=root_window, offset_y=lambda lines: lines // 2 - 3
            )
            self.input_label = Label(
                parent_win=root_window, offset_y=lambda lines: lines // 2 + 3
            )
            self.input = Input(parent_win=root_window, callback=key_input_callback)
            self.input_border = InputBorder(parent_win=root_window)
            self.score = Label(
                parent_win=root_window, offset_y=lambda lines: lines // 2 + 6
            )
            self.all = [
                self.main,
                self.guess_result,
                self.statusbar,
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
            white = curses.COLOR_WHITE
            gray = curses.COLOR_BLACK
            if curses.COLORS >= 16:
                white += 8
                gray += 8
            curses.init_pair(1, white, curses.COLOR_BLUE)
            curses.init_pair(2, curses.COLOR_BLACK, white)
            curses.init_pair(3, white, gray)
        self._windows = self._Windows(self._stdscr, self._key_input)

    # Ignore invalid name for ch (we're reusing the existing name from the curses module)
    # pylint: disable=invalid-name
    def _key_input(self, ch):
        if ch == curses.KEY_RESIZE:
            for win in self._windows.all:
                win.redraw()

    def display_flashcard(
        self, index: int, total: int, flashcard: str, max_key_length: int
    ):
        self._windows.statusbar.set_text(
            text=self.translations("progress").format(index=index, total=total),
        )

        # make sure the flashcard width and input box with are both multiples of
        # 2, so they'll be alignedhorizontally.
        flashcard_width = max_key_length + 8
        if flashcard_width % 2 != 0:
            flashcard_width += 1

        self._windows.card_bkgd.width = flashcard_width
        self._windows.card_bkgd.redraw()
        self._windows.card_text.set_text(
            text=self.translations("display_flashcard").format(key=flashcard),
            color_pair=curses.color_pair(2),
        )

    async def input_guess(self, flashcard: str, max_answer_length: int) -> str:
        input_width = max_answer_length + 1
        if input_width % 2 != 0:
            input_width += 1
        self._windows.input_border.width = input_width
        self._windows.input_border.redraw()
        self._windows.input.width = input_width
        self._windows.input.redraw(text="")
        return self._windows.input.wait_for_string()

    async def input_replay_missed_cards(self) -> bool:
        self._windows.input_label.set_text(
            text=self.translations("play_again"),
            color_attrs=curses.A_BLINK,
        )
        self._windows.input.hide()
        self._windows.input_border.hide()
        self._windows.input_label.win.move(0, 0)
        self._windows.input_label.redraw()
        safe_curses_curs_set(0)
        key = self._windows.input.wait_for_key()
        do_replay = key.casefold() == self.translations("answer_yes").casefold()
        safe_curses_curs_set(1)
        self._windows.score.hide()
        self._windows.input_label.hide()
        self._windows.guess_result.hide()
        if do_replay:
            self._windows.input.show()
            self._windows.input_border.show()
        return do_replay

    def display_right_guess(self, key: str, correct_answer: str):
        self._windows.guess_result.set_text(text=self.translations("right_guess"))

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
        safe_curses_curs_set(0)
        try:
            self._windows.input.wait_for_key()
        except (KeyboardInterrupt, EOFError):
            pass
        safe_curses_curs_set(1)
        curses.nocbreak()
        self._stdscr.keypad(False)
        curses.echo()
        curses.endwin()
