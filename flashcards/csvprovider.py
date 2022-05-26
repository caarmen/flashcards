"""
Read flashcards from a csv file
"""
import csv

from flashcards.provider import FlashcardProvider


# pylint: disable=too-few-public-methods
class CsvFlashcardProvider(FlashcardProvider):
    """
    Provide flashcards from a csv file
    """

    def __init__(self, file):
        self.cards = {}
        with file as csvfile:
            reader = csv.reader(csvfile)
            self.cards = {row[0]: row[1] for row in reader}

    def flashcards(self) -> dict[str, str]:
        return self.cards
