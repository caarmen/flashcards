"""
Flashcards engine
"""
import random

from flashcards.provider import FlashcardProvider
from flashcards.ui import Ui


class Engine:
    """
    Flashcards engine
    """

    def __init__(self, game_ui: Ui, provider: FlashcardProvider):
        self.game_ui = game_ui
        self.correct_count = 0
        self.guessed_count = 0
        self.provider = provider

    async def play(self):
        """
        Play a game
        """
        flashcards = self.provider.flashcards()
        keys = list(flashcards.keys())
        random.shuffle(keys)
        self.correct_count = 0
        self.guessed_count = 0
        for index, key in enumerate(keys):
            self.game_ui.display_flashcard(index=index, total=len(keys), flashcard=key)
            guess = await self.game_ui.input_guess(key)
            correct_answer = flashcards[key]
            if guess == correct_answer:
                self.correct_count += 1
                self.game_ui.display_right_guess(key, guess)
            else:
                self.game_ui.display_wrong_guess(key, guess, correct_answer)
            self.guessed_count += 1
        self.game_ui.display_score(self.correct_count, self.guessed_count)

    async def game_interrupted(self):
        """
        Handle the interruption of the game by the user
        """
        self.game_ui.display_score(self.correct_count, self.guessed_count)
