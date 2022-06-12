"""
Application entry point
"""
import argparse
import gettext
import os
import sys
from os import path

from flashcards.csvprovider import CsvFlashcardProvider
from flashcards.cursesui.cursesui import CursesUi
from flashcards.engine import Engine
from flashcards.textualui import TextualUi
from flashcards.textui import TextUi

BUNDLE_DIR = getattr(
    sys, "_MEIPASS", path.abspath(path.dirname(path.dirname(__file__)))
)
locales_dir = path.abspath(path.join(BUNDLE_DIR, "locales"))

translations = gettext.translation(
    "base", localedir=locales_dir, languages=[os.environ.get("LANG", "en")]
)
translations.install()
_ = translations.gettext


def main():
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
        default="textual",
        choices=["text", "curses", "textual"],
        help="Ui type. Default is %(default)s",
    )
    options = parser.parse_args()

    match options.ui:
        case "curses":
            game_ui = CursesUi(_)
        case "textual":
            game_ui = TextualUi(_)
        case _:
            game_ui = TextUi(_)
    provider = CsvFlashcardProvider(options.input)
    engine = Engine(game_ui, provider)
    try:
        engine.play()
    except (KeyboardInterrupt, EOFError):
        engine.game_interrupted()
