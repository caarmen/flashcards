"""
Console user interface
"""
from flashcards.ui import Ui


class ConsoleUi(Ui):
    """
    Interface to interact with the user in the flashcard game, in a console
    """

    def __init__(self, translations):
        self.translations = translations

    def display_flashcard(self, index: int, total: int, flashcard: str):
        print(
            self.translations("display_flashcard").format(
                index=index, total=total, key=flashcard
            )
        )

    async def input_guess(self, flashcard: str) -> str:
        return input(self.translations("guess_prompt"))

    def display_right_guess(self, key: str, correct_answer: str):
        print(self.translations("right_guess"))

    def display_wrong_guess(self, key: str, guess: str, correct_answer: str):
        print(self.translations("wrong_guess").format(correct_answer=correct_answer))

    def display_score(self, correct_count: int, guessed_count: int):
        print(
            self.translations("game_score").format(
                correct_count=correct_count, guessed_count=guessed_count
            )
        )
