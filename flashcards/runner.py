"""
Application entry point
"""
import argparse
import gettext
import os

from flashcards.consoleui import ConsoleUi
from flashcards.engine import Engine
from flashcards.csvprovider import CsvFlashcardProvider

translations = gettext.translation(
    "base", localedir="locales", languages=[os.environ.get("LANG", "en")]
)
translations.install()
_ = translations.gettext


async def main():
    """
    Application entry point
    """
    parser = argparse.ArgumentParser(description="Flashcards game")
    parser.add_argument(
        "input",
        metavar="flashcards_csv_file",
        type=argparse.FileType("r"),
        help="Path to flashcards csv file",
    )
    options = parser.parse_args()

    game_ui = ConsoleUi(_)
    provider = CsvFlashcardProvider(options.input)
    engine = Engine(game_ui, provider)
    try:
        await engine.play()
    except (KeyboardInterrupt, EOFError):
        await engine.game_interrupted()
