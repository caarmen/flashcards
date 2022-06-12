"""
Provider tests
"""
import gettext
from os import path

import pytest

from flashcards.provider import FlashcardProvider
from tests.fakes import FakeCursesUi, FakeUi, FakeFlashcardProvider, FakeTextualUi


@pytest.fixture(name="ui_factory")
def fixture_ui_factory():
    """
    :return: Factory to create a Ui with hardcoded guesses
    """

    def _make_ui(guesses: dict[str:str]) -> FakeUi:
        return FakeUi(guesses=guesses)

    return _make_ui


@pytest.fixture(name="textual_ui_factory")
def fixture_textual_ui_factory(translations):
    """
    :return: Factory to create a textual Ui with hardcoded guesses
    """

    def _make_textual_ui(guesses: dict[str:str]) -> FakeTextualUi:
        return FakeTextualUi(translations=translations, guesses=guesses)

    return _make_textual_ui


@pytest.fixture(name="curses_ui_factory")
def fixture_curses_ui_factory(translations):
    """
    :return: Factory to create a curses Ui with hardcoded guesses
    """

    def _make_curses_ui(guesses: dict[str:str]) -> FakeCursesUi:
        return FakeCursesUi(translations=translations, guesses=guesses)

    return _make_curses_ui


@pytest.fixture(name="provider_factory")
def fixture_provider_factory():
    """
    :return: Factory to create a FlashcardProvider with hardcoded flashcard data
    """

    def _make_provider(flashcards: dict[str, str]) -> FlashcardProvider:
        return FakeFlashcardProvider(flashcards)

    return _make_provider


@pytest.fixture(name="translations")
def fixture_translations():
    """
    Loads translations and provides the translation function
    :return: translations gettext function
    """
    locales_dir = path.abspath(
        path.join(path.dirname(path.dirname(__file__)), "locales")
    )
    translations = gettext.translation("base", localedir=locales_dir, languages=["en"])
    translations.install()
    return translations.gettext
