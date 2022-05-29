"""
Curses-based console user interface
"""
import curses
from dataclasses import dataclass
from typing import Callable

from flashcards.cursesui.safe_curses import safe_curses_curs_set, safe_curses_endwin, safe_curses_nocbreak
from flashcards.cursesui.widgets import (
    Background,
    Label,
    Card,
    Input,
    InputBorder,
    StatusBar,
)
from flashcards.ui import Ui


@dataclass
class Palette:
    """
    Provide colors for different components of the app
    """

    default_color: int
    card_color: int
    statusbar_color: int
    input_color: int

    def __init__(self):
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
            curses.init_pair(4, white, curses.COLOR_BLACK)
        self.default_color = curses.color_pair(1)
        self.card_color = curses.color_pair(2)
        self.statusbar_color = curses.color_pair(3)
        self.input_color = curses.color_pair(4)


# pylint: disable=too-few-public-methods,too-many-instance-attributes
class Widgets:
    """
    Collection of the different widgets used in the app
    """

    def __init__(self, key_input_callback: Callable[[int], None]):
        # pylint: disable=no-member
        root_window = curses.initscr()
        palette = Palette()
        self.main = Background(root_window, color_pair=palette.default_color)
        self.guess_result = Label(
            parent_win=root_window,
            color_pair=palette.default_color,
            offset_y=lambda lines: lines // 2 - 8,
        )
        self.statusbar = StatusBar(
            parent_win=root_window,
            background_color_pair=palette.default_color,
            status_bar_color_pair=palette.statusbar_color,
        )
        self.card_bkgd = Card(
            parent_win=root_window,
            background_color_pair=palette.default_color,
            card_color_pair=palette.card_color,
        )
        self.card_text = Label(
            parent_win=root_window,
            color_pair=palette.card_color,
            offset_y=lambda lines: lines // 2 - 3,
        )
        self.input_label = Label(
            parent_win=root_window,
            color_pair=palette.default_color,
            color_attrs=curses.A_BLINK,
            offset_y=lambda lines: lines // 2 + 3,
        )
        self.input = Input(
            parent_win=root_window,
            color_pair=palette.default_color,
            input_color_pair=palette.input_color,
            callback=key_input_callback,
        )
        self.input_border = InputBorder(
            parent_win=root_window,
            color_pair=palette.default_color,
            input_color_pair=palette.input_color,
        )
        self.score = Label(
            parent_win=root_window,
            color_pair=palette.default_color,
            color_attrs=curses.A_UNDERLINE,
            offset_y=lambda lines: lines // 2 + 6,
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


class CursesUi(Ui):
    """
    Interact with the user in the flashcard game, in a console using curses
    """

    def __init__(self, translations):
        self.translations = translations
        self._widgets = Widgets(self._on_key_input)
        curses.noecho()

    # Ignore invalid name for ch (we're reusing the existing name from the curses module)
    # pylint: disable=invalid-name
    def _on_key_input(self, ch):
        if ch == curses.KEY_RESIZE:
            for win in self._widgets.all:
                win.redraw()

    def display_flashcard(
            self, index: int, total: int, flashcard: str, max_key_length: int
    ):
        self._widgets.statusbar.set_text(
            text=self.translations("progress").format(index=index, total=total),
        )

        # make sure the flashcard width and input box with are both multiples of
        # 2, so they'll be alignedhorizontally.
        flashcard_width = max_key_length + 8
        if flashcard_width % 2 != 0:
            flashcard_width += 1

        self._widgets.card_bkgd.width = flashcard_width
        self._widgets.card_bkgd.redraw()
        self._widgets.card_text.set_text(
            text=self.translations("display_flashcard").format(key=flashcard)
        )

    async def input_guess(self, flashcard: str, max_answer_length: int) -> str:
        input_width = max_answer_length + 1
        if input_width % 2 != 0:
            input_width += 1
        self._widgets.input_border.width = input_width
        self._widgets.input_border.redraw()
        self._widgets.input.width = input_width
        self._widgets.input.redraw(text="")
        return self._widgets.input.wait_for_string()

    async def input_replay_missed_cards(self) -> bool:
        self._widgets.input_label.set_text(text=self.translations("play_again"))
        self._widgets.input.hide()
        self._widgets.input_border.hide()
        self._widgets.input_label.win.move(0, 0)
        self._widgets.input_label.redraw()
        safe_curses_curs_set(0)
        key = self._widgets.input.wait_for_key()
        do_replay = key.casefold() == self.translations("answer_yes").casefold()
        safe_curses_curs_set(1)
        self._widgets.score.hide()
        self._widgets.input_label.hide()
        self._widgets.guess_result.hide()
        if do_replay:
            self._widgets.input.show()
            self._widgets.input_border.show()
        return do_replay

    def display_right_guess(self, key: str, correct_answer: str):
        self._widgets.guess_result.set_text(text=self.translations("right_guess"))

    def display_wrong_guess(self, key: str, guess: str, correct_answer: str):
        self._widgets.guess_result.set_text(
            text=self.translations("wrong_guess").format(correct_answer=correct_answer),
        )

    def display_score(self, correct_count: int, guessed_count: int):
        self._widgets.score.set_text(
            text=self.translations("game_score").format(
                correct_count=correct_count, guessed_count=guessed_count
            )
        )

    def game_over(self):
        safe_curses_curs_set(0)
        try:
            self._widgets.input.wait_for_key()
        except (KeyboardInterrupt, EOFError):
            pass
        safe_curses_curs_set(1)
        safe_curses_nocbreak()
        curses.echo()
        safe_curses_endwin()
