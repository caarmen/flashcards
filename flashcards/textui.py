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
        self._ = translator

    def display_flashcard(
        self, index: int, total: int, flashcard: str, max_key_length: int
    ):
        print(self._("progress").format(index=index, total=total))
        print(self._("display_flashcard").format(key=flashcard))

    def input_guess(self, flashcard: str, max_answer_length: int) -> str:
        return input(self._("guess_prompt"))

    def input_replay_missed_cards(self) -> bool:
        return input(self._("play_again")).casefold() == self._("answer_yes").casefold()

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
