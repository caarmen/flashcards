"""
Simple text console user interface
"""
import asyncio
from typing import Callable

from rich import box
from rich.console import RenderableType
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text
from textual import events
from textual.app import App
from textual.widget import Widget
from textual_inputs import TextInput

from flashcards.ui import Ui

Translator = Callable[[str], str]


class FlashcardWidget(Widget):
    """
    Widget to display the revealed part of a flashcard
    """

    def __init__(self):
        super().__init__()
        self.text = ""
        self.max_text_size = 0

    def render(self) -> RenderableType:
        inner_padding_horizontal = 5
        inner_padding_vertical = 1
        box_border_thickness = 1
        outer_padding_horizontal = (
            ((self.size.width - self.max_text_size) // 2)
            - inner_padding_horizontal
            - 2 * box_border_thickness
        )
        outer_padding_vertical = (
            ((self.size.height - 1) // 2)
            - inner_padding_vertical
            - 2 * box_border_thickness
        )
        return Padding(
            renderable=Panel(
                box=box.HEAVY,
                style="bold black on bright_white",
                renderable=Padding(
                    renderable=Text(
                        text=self.text,
                        justify="center",
                    ),
                    pad=(
                        inner_padding_vertical,
                        inner_padding_horizontal,
                        inner_padding_vertical,
                        inner_padding_horizontal,
                    ),
                ),
            ),
            pad=(
                outer_padding_vertical,
                outer_padding_horizontal,
                outer_padding_vertical,
                outer_padding_horizontal,
            ),
            style="bright_white on bright_blue",
        )


class InfoPane(Widget):
    """
    Widget to show one line of text information
    """

    default_style_text = "bright_white on bright_blue"
    blink_style_text = f"blink {default_style_text}"

    def __init__(self):
        super().__init__()
        self.text = ""
        self.style_text = InfoPane.default_style_text

    def blink(self, enabled):
        """
        Turn blink on or off for the text in this pane
        """
        self.style_text = (
            InfoPane.blink_style_text if enabled else InfoPane.default_style_text
        )
        self.refresh()

    def render(self) -> RenderableType:
        return Padding(
            pad=(1, 0, 1, 0),
            renderable=Text(
                text=self.text,
                justify="center",
            ),
            # colors: https://github.com/Textualize/rich/blob/master/docs/source/appendix/colors.rst
            style=self.style_text,
        )


class StatusBar(Widget):
    """
    Status bar widget
    """

    def __init__(self):
        super().__init__()
        self.text = ""

    def render(self) -> RenderableType:
        return Padding(
            renderable=Text(
                text=self.text,
                justify="right",
            ),
            pad=(0, 1, 0, 0),
            # colors: https://github.com/Textualize/rich/blob/master/docs/source/appendix/colors.rst
            style="bright_white on bright_black",
        )


class TextualUi(Ui, App):
    """
    Interface to interact with the user in the flashcard game, in a console,
    using the textual library
    """

    def __init__(self, translator: Translator):
        Ui.__init__(self)
        App.__init__(self, True, None, log="foo.txt")
        self._ = translator
        self.flashcard_text = ""
        self.text_input = TextInput(
            name="",
            placeholder=self._("guess_prompt"),
            title="",
        )
        self.flashcard = FlashcardWidget()
        self.info_pane1 = InfoPane()
        self.info_pane2 = InfoPane()
        self.status_bar = StatusBar()

    async def on_mount(self) -> None:
        """
        Layout the UI
        """
        await self.view.dock(self.status_bar, edge="bottom", size=1)
        await self.view.dock(self.info_pane2, edge="bottom", size=5)
        await self.view.dock(self.text_input, edge="bottom", size=3)
        await self.view.dock(self.info_pane1, edge="top", size=5)
        await self.view.dock(self.flashcard, edge="top")
        await self.text_input.focus()

    def setup(self, max_key_length: int, max_answer_length: int):
        self.flashcard.max_text_size = max_key_length

    def new_game(self):
        self.info_pane1.text = ""
        self.info_pane2.text = ""
        self.info_pane2.blink(False)
        self.text_input.value = ""
        self.text_input.visible = True
        self.info_pane1.refresh()
        self.info_pane2.refresh()
        self.text_input.refresh()

    def display_flashcard(self, index: int, total: int, flashcard: str):
        self.text_input.value = ""
        self.flashcard.text = flashcard
        self.status_bar.text = self._("progress").format(index=index, total=total)
        self.status_bar.refresh()
        self.flashcard.refresh()
        self._run_if_needed()

    def _run_if_needed(self):
        if not self.is_running:
            asyncio.run(self.process_messages())

    async def action_submit(self) -> None:
        """
        Called when the user types enter
        """
        self.input_callback.on_guess(self.text_input.value)

    async def on_load(self) -> None:
        """
        Set up key bindings
        """
        await self.bind("q", "quit", "Quit")
        await self.bind("enter", "submit", "Submit")

    def prompt_replay_missed_cards(self):
        self.text_input.value = ""
        self.text_input.refresh()
        self.text_input.visible = False
        self.info_pane2.text = self._("play_again")
        self.info_pane2.blink(True)
        self.info_pane2.refresh()

    async def on_event(self, event: events.Event) -> None:
        await super().on_event(event)
        if isinstance(event, events.Key):
            if not self.text_input.visible:
                self._on_replay_answer(event.key)

    def _on_replay_answer(self, key: str):
        if key.casefold() == self._("answer_yes").casefold():
            self.input_callback.on_replay_answer(True)
        elif key.casefold() == self._("answer_no").casefold():
            self.input_callback.on_replay_answer(False)
        # else ignore

    def display_right_guess(self, key: str, correct_answer: str):
        self.info_pane1.text = self._("right_guess")
        self.info_pane1.refresh()

    def display_wrong_guess(self, key: str, guess: str, correct_answer: str):
        self.info_pane1.text = self._("wrong_guess").format(
            correct_answer=correct_answer
        )
        self.info_pane1.refresh()

    def display_score(self, correct_count: int, guessed_count: int):
        self.info_pane2.text = self._("game_score").format(
            correct_count=correct_count, guessed_count=guessed_count
        )
        self.info_pane2.refresh()

    def game_over(self):
        self.close_messages_no_wait()
