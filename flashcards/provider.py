"""
Interface to provide flashcards
"""
import abc


# pylint: disable=too-few-public-methods
class FlashcardProvider(metaclass=abc.ABCMeta):
    """
    Interface to provide flashcards
    """

    @abc.abstractmethod
    def flashcards(self) -> dict[str, str]:
        """
        :return: a mapping of flashcards: one side mapped to the other side
        """
