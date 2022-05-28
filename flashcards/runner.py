"""
Application entry point
"""
import argparse
import gettext
import os
from os import path
import sys

from flashcards.cursesui.cursesui import CursesUi
from flashcards.textui import TextUi
from flashcards.engine import Engine
from flashcards.csvprovider import CsvFlashcardProvider

BUNDLE_DIR = getattr(
    sys, "_MEIPASS", path.abspath(path.dirname(path.dirname(__file__)))
)
locales_dir = path.abspath(path.join(BUNDLE_DIR, "locales"))

translations = gettext.translation(
    "base", localedir=locales_dir, languages=[os.environ.get("LANG", "en")]
)
translations.install()
_ = translations.gettext


async def main():
    """
    Application entry point
    """
    parser = argparse.ArgumentParser(prog="flashcards", description="Flashcards game")
    parser.add_argument(
        "input",
        metavar="flashcards_csv_file",
        type=argparse.FileType("r"),
        help="Path to flashcards csv file",
    )
    parser.add_argument(
        "--ui",
        nargs="?",
        default="curses",
        choices=["text", "curses"],
        help="Ui type. Default is %(default)s",
    )
    options = parser.parse_args()

    if options.ui == "curses":
        game_ui = CursesUi(_)
    else:
        game_ui = TextUi(_)
    provider = CsvFlashcardProvider(options.input)
    engine = Engine(game_ui, provider)
    try:
        await engine.play()
    except (KeyboardInterrupt, EOFError):
        await engine.game_interrupted()
