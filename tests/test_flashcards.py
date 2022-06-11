"""
Flashcard tests
"""

from flashcards.csvprovider import CsvFlashcardProvider
from flashcards.engine import Engine


def test_csv_provider(tmp_path):
    """
    Check that we are able to read flashcards from a csv file
    """
    input_text = """hello,bonjour
goodbye,au revoir"""
    input_file = tmp_path / "input.csv"
    input_file.write_text(input_text)

    with open(input_file, encoding="utf-8") as csv_file:
        provider = CsvFlashcardProvider(csv_file)
    flashcards = provider.flashcards()
    assert flashcards["hello"] == "bonjour"
    assert flashcards["goodbye"] == "au revoir"


def test_engine_score(provider_factory, ui_factory):
    """
    Test that the engine calculates the expected score
    """

    provider = provider_factory({"hello": "hola", "goodbye": "adiós", "cold": "frío"})
    game_ui = ui_factory({"hello": "hola", "goodbye": "au revoir", "cold": "frío"})
    engine = Engine(game_ui=game_ui, provider=provider)
    engine.play()
    assert game_ui.guessed_count == 3
    assert game_ui.correct_count == 2


def test_curses_engine_score(provider_factory, curses_ui_factory):
    """
    Test that the engine calculates the expected score with a curses ui
    """

    provider = provider_factory({"hello": "hola", "goodbye": "adios", "cold": "frio"})
    game_ui = curses_ui_factory(
        guesses={"hello": "hola", "goodbye": "au revoir", "cold": "frio"}
    )
    engine = Engine(game_ui=game_ui, provider=provider)
    engine.play()
    assert game_ui.guessed_count == 3
    assert game_ui.correct_count == 2
