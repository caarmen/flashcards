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

    async def _play_deck(self, deck: dict[str, str], max_answer_length: int):
        keys = list(deck.keys())
        random.shuffle(keys)
        self.correct_count = 0
        self.guessed_count = 0
        wrong_guesses = {}
        for index, key in enumerate(keys):
            self.game_ui.display_flashcard(
                index=index + 1, total=len(keys), flashcard=key
            )
            guess = (await self.game_ui.input_guess(key, max_answer_length)).strip()
            correct_answer = deck[key]
            if guess.casefold() == correct_answer.casefold():
                self.correct_count += 1
                self.game_ui.display_right_guess(key, guess)
            else:
                self.game_ui.display_wrong_guess(key, guess, correct_answer)
                wrong_guesses[key] = correct_answer
            self.guessed_count += 1
        self.game_ui.display_score(self.correct_count, self.guessed_count)
        if wrong_guesses:
            if await self.game_ui.input_replay_missed_cards():
                await self._play_deck(wrong_guesses, max_answer_length)

    async def play(self):
        """
        Play a game
        """
        flashcards = self.provider.flashcards()
        max_answer_length = max([len(x) for x in flashcards.values()])
        await self._play_deck(flashcards, max_answer_length)
        self.game_ui.game_over()

    async def game_interrupted(self):
        """
        Handle the interruption of the game by the user
        """
        self.game_ui.display_score(self.correct_count, self.guessed_count)
        self.game_ui.game_over()
