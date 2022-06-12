"""
Flashcards engine
"""
import random
from dataclasses import dataclass

from flashcards.provider import FlashcardProvider
from flashcards.ui import Ui


class Engine:
    """
    Flashcards engine
    """

    @dataclass
    class _State:
        """
        Represents the state of the flashcard game
        """

        remaining_cards: dict[str:str]
        missed_cards: dict[str:str]
        current_card_key: str
        correct_count: int = 0
        guessed_count: int = 0

    def __init__(self, game_ui: Ui, provider: FlashcardProvider):
        self.game_ui = game_ui
        self.game_ui.input_callback = self
        self.provider = provider
        self._state = Engine._State(
            remaining_cards={}, missed_cards={}, current_card_key=""
        )

    def on_guess(self, raw_guess: str):
        """
        Called when the user has submitted a guess for a flashcard.
        """
        correct_answer = self._state.remaining_cards.pop(self._state.current_card_key)
        guess = raw_guess.strip().casefold()
        if guess == correct_answer.casefold():
            self._state.correct_count += 1
            self.game_ui.display_right_guess(self._state.current_card_key, guess)
        else:
            self.game_ui.display_wrong_guess(
                self._state.current_card_key, guess, correct_answer
            )
            self._state.missed_cards[self._state.current_card_key] = correct_answer
        self._state.guessed_count += 1
        self.game_ui.display_score(self._state.correct_count, self._state.guessed_count)

        if self._state.remaining_cards:
            self._play_next_card()
        else:
            self._on_end_of_round()

    def on_replay_answer(self, answer: bool):
        """
        Called when the user has chosen to replay or not the missed cards.
        """
        if answer:
            self._play_deck(self._state.missed_cards)
        else:
            self.game_ui.game_over()

    def _play_next_card(self):
        self._state.current_card_key = random.choice(
            list(self._state.remaining_cards.keys())
        )
        self.game_ui.display_flashcard(
            index=self._state.guessed_count + 1,
            total=self._state.guessed_count + len(self._state.remaining_cards),
            flashcard=self._state.current_card_key,
        )

    def _on_end_of_round(self):
        if self._state.missed_cards:
            self.game_ui.prompt_replay_missed_cards()
        else:
            self.game_ui.game_over()

    def _play_deck(self, deck: dict[str, str]):
        self._state = Engine._State(
            remaining_cards=deck,
            missed_cards={},
            current_card_key=random.choice(list(deck.keys())),
        )
        self.game_ui.new_game()
        self._play_next_card()

    def play(self):
        """
        Play a game
        """
        flashcards = self.provider.flashcards()
        max_key_length = max([len(x) for x in flashcards.keys()])
        max_answer_length = max([len(x) for x in flashcards.values()])
        self.game_ui.setup(
            max_key_length=max_key_length, max_answer_length=max_answer_length
        )
        self._play_deck(flashcards)

    def game_interrupted(self):
        """
        Handle the interruption of the game by the user
        """
        self.game_ui.display_score(self._state.correct_count, self._state.guessed_count)
        self.game_ui.game_over()
