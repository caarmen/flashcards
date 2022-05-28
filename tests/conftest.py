"""
Provider tests
"""

import pytest

from flashcards.provider import FlashcardProvider
from flashcards.ui import Ui


@pytest.fixture(name="ui_factory")
def fixture_ui_factory():
    """
    :return: Factory to create a Ui with hardcoded guesses
    """

    class TestUi(Ui):
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

    def _make_ui(guesses: dict[str:str]) -> TestUi:
        return TestUi(guesses=guesses)

    return _make_ui


@pytest.fixture(name="provider_factory")
def fixture_provider_factory():
    """
    :return: Factory to create a FlashcardProvider with hardcoded flashcard data
    """

    # pylint: disable=too-few-public-methods
    class TestFlashcardProvider(FlashcardProvider):
        """
        Test flashcard provider with hardcoded flashcards
        """

        def __init__(self, cards: dict[str:str]):
            self.cards = cards

        def flashcards(self) -> dict[str, str]:
            return self.cards

    def _make_provider(flashcards: dict[str, str]) -> FlashcardProvider:
        return TestFlashcardProvider(flashcards)

    return _make_provider
