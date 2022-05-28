"""
Add some support for unicode to Textbox
"""
import curses
from curses.ascii import isprint, iscntrl
from curses.textpad import Textbox

from flashcards.cursesui.utils import safe_win_addch


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
        safe_win_addch(ch)
        return 1

    def gather(self) -> str:
        return self.win.instr(0, 0).decode("utf-8")
