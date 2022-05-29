"""
Provide fake implementations of classes for tests
"""
import curses

from flashcards.cursesui.cursesui import CursesUi
from flashcards.provider import FlashcardProvider
from flashcards.ui import Ui


# pylint: disable=too-few-public-methods
class FakeFlashcardProvider(FlashcardProvider):
    """
    Test flashcard provider with hardcoded flashcards
    """

    def __init__(self, cards: dict[str:str]):
        self.cards = cards

    def flashcards(self) -> dict[str, str]:
        return self.cards


class FakeUi(Ui):
    """
    Test flashcard ui which immediately returns test guesses
    """

    def __init__(self, guesses: dict[str:str]):
        self.correct_count = 0
        self.guessed_count = 0
        self.guesses = guesses

    def display_flashcard(
        self, index: int, total: int, flashcard: str, max_key_length: int
    ):
        pass

    def display_right_guess(self, key: str, correct_answer: str):
        pass

    def display_wrong_guess(self, key: str, guess: str, correct_answer: str):
        pass

    async def input_guess(self, flashcard: str, max_answer_length: int) -> str:
        return self.guesses.get(flashcard)

    async def input_replay_missed_cards(self) -> bool:
        return False

    def display_score(self, correct_count: int, guessed_count: int):
        self.correct_count = correct_count
        self.guessed_count = guessed_count


class FakeCursesUi(CursesUi):
    """
    Simlate a curses ui. The user input is done with calls to ungetch
    """

    def __init__(self, translations, guesses: dict[str:str]):
        super().__init__(translations)
        self.correct_count = 0
        self.guessed_count = 0
        self.guesses = guesses

    @staticmethod
    def _fake_user_input(text: str):
        for char in text[::-1]:
            curses.ungetch(ord(char))

    async def input_guess(self, flashcard: str, max_answer_length: int) -> str:
        guess = self.guesses.get(flashcard)
        self._fake_user_input(f"{guess}\n")
        return await super().input_guess(flashcard, max_answer_length)

    async def input_replay_missed_cards(self) -> bool:
        self._fake_user_input("n")  # No, to not replay the missed cards
        self._fake_user_input("x")  # x, any key to exit the game
        return await super().input_replay_missed_cards()

    def display_score(self, correct_count: int, guessed_count: int):
        self.correct_count = correct_count
        self.guessed_count = guessed_count
        super().display_score(correct_count=correct_count, guessed_count=guessed_count)
