"""
Simple text console user interface
"""
from typing import Callable

from flashcards.ui import Ui

Translator = Callable[[str], str]


class TextUi(Ui):
    """
    Interface to interact with the user in the flashcard game, in a console,
    using simple text input/output
    """

    def __init__(self, translator: Translator):
        super().__init__()
        self._ = translator

    def display_flashcard(self, index: int, total: int, flashcard: str):
        print(self._("progress").format(index=index, total=total))
        print(self._("display_flashcard").format(key=flashcard))
        guess = input(self._("guess_prompt"))
        self.input_callback.on_guess(guess)

    def prompt_replay_missed_cards(self):
        continue_answer = (
            input(self._("play_again")).casefold() == self._("answer_yes").casefold()
        )
        self.input_callback.on_replay_answer(continue_answer)

    def display_right_guess(self, key: str, correct_answer: str):
        print(self._("right_guess"))

    def display_wrong_guess(self, key: str, guess: str, correct_answer: str):
        print(self._("wrong_guess").format(correct_answer=correct_answer))

    def display_score(self, correct_count: int, guessed_count: int):
        print(
            self._("game_score").format(
                correct_count=correct_count, guessed_count=guessed_count
            )
        )
