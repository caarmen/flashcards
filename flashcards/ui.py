"""
Define the Ui functions for the flashcard game
"""
import abc


class Ui(metaclass=abc.ABCMeta):
    """
    Interface to interact with the user in the flashcard game
    """

    @abc.abstractmethod
    def display_flashcard(self, index: int, total: int, flashcard: str):
        """
        Display the flashcard
        """

    @abc.abstractmethod
    async def input_guess(self, flashcard: str) -> str:
        """
        Input the user's guess for the given flaskcard
        """

    @abc.abstractmethod
    async def input_replay_missed_cards(self) -> bool:
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
