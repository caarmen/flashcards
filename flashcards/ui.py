"""
Define the Ui functions for the flashcard game
"""
import abc
from typing import Protocol


class SupportsInputCallback(Protocol):
    """
    Callbacks from user input
    """

    def on_guess(self, raw_guess: str):
        """
        Called when the user has submitted a guess for a flashcard.
        """

    def on_replay_answer(self, answer: bool):
        """
        Called when the user has chosen to replay or not the missed cards.
        """


class Ui(metaclass=abc.ABCMeta):
    """
    Interface to interact with the user in the flashcard game
    """

    def __init__(self):
        self.input_callback = None

    def setup(self, max_key_length: int, max_answer_length: int):
        """
        Setup the ui
        """

    def new_game(self):
        """
        Start a new game
        """

    @abc.abstractmethod
    def display_flashcard(self, index: int, total: int, flashcard: str):
        """
        Display the flashcard
        """

    @abc.abstractmethod
    def prompt_replay_missed_cards(self):
        """
        Ask the user if they want to replay the cards they missed
        """

    @abc.abstractmethod
    def display_right_guess(self, key: str, correct_answer: str):
        """
        :param key: the flashcard side initially displayed
        :param correct_answer: the other side of the flashcard
        """

    @abc.abstractmethod
    def display_wrong_guess(self, key: str, guess: str, correct_answer: str):
        """
        :param key: the flashcard side initially displayed
        :param guess: what the user guessed
        :param correct_answer: the other side of the flashcard
        """

    @abc.abstractmethod
    def display_score(self, correct_count: int, guessed_count: int):
        """
        Display the score of a game
        """

    def game_over(self):
        """
        Handle any cleanup at the end of the game
        """
