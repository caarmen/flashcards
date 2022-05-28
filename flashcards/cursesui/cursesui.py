"""
Curses-based console user interface
"""
import curses

from flashcards.cursesui.windows import _BackgroundWindow, _TextWindow, _FlashcardBackground, _Input, _InputBorder
from flashcards.cursesui.unicodetextbox import UnicodeTextbox
from flashcards.ui import Ui


class CursesUi(Ui):
    """
    Interact with the user in the flashcard game, in a console using curses
    """

    # pylint: disable=too-few-public-methods,too-many-instance-attributes
    class _Windows:
        def __init__(self, root_window):
            # pylint: disable=no-member
            self.main = _BackgroundWindow(root_window, color_pair=curses.color_pair(1))
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

    def _display_input_box(self, length: int):
        self._windows.input_border.width = length
        self._windows.input_border.set_text("")
        self._windows.input.width = length
        self._windows.input.set_text("")

    def _horse(self, ch):
        if ch == 127:
            return curses.KEY_BACKSPACE
        if ch == curses.KEY_RESIZE:
            self._windows.main.redraw()
            for win in self._windows.text_windows:
                win.redraw()
        return ch

    def _input_text(self, length: int) -> str:
        self._display_input_box(length=length)
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
        return self._input_text(length=input_width)

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
