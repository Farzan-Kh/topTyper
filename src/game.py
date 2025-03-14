import random

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Static, Input, DataTable
from textual.reactive import reactive
from utils import calculate_wpm, calculate_accuracy
from rich.text import Text
from models.player import Player
from textual.timer import Timer


class SpeedTypingApp(App):
    CSS_PATH = "../resources/styles/styles.css"

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.sample_text = self.generate_sample_text()
        self.username = reactive("")
        self.typed_text = reactive("")
        self.start_time = None
        self.banner_text = self.load_banner()

    def load_banner(self):
        """
        Load the banner text from the banner.txt file.
        """
        try:
            with open("banner.txt", "r") as file:
                return file.read()
        except FileNotFoundError:
            return "Welcome to the Speed Typing Contest!"

    def generate_sample_text(self, length=20):
        """
        Generate a random sentence from words in the words.txt file.
        """
        try:
            with open("resources/words/words.txt", "r") as file:
                words = [word.strip() for word in file.readlines() if word.strip()]
                if len(words) < length:
                    raise ValueError("Not enough words in words.txt to generate a sentence.")
                return Text(" ".join(random.choices(words, k=length)), style="bold")
        except FileNotFoundError:
            return "Error: words.txt file not found."
        except ValueError as e:
            return str(e)

    def compose(self) -> ComposeResult:
        yield Container(
            Static("Speed Typing Contest", id="header"),
            Static(self.banner_text, id="banner", classes="margin-bottom"),
            Static("", id="countdown-label", classes="hidden margin-bottom"),  # Countdown label
            Static(self.sample_text, id="text-to-type", classes="hidden"),  # Initially hidden
            Static("Please input your Username:", id="username-label", classes="margin-bottom"),
            Input(placeholder="Enter your username and press Enter", id="username-input"),
            Static("Please input the text above:", id="text-label", classes="hidden margin-bottom"),
            Input(placeholder="Type here and press Enter to finish", id="typing-input", classes="hidden"),
            id="left-pane",
        )
        yield Container(
            Static("Leaderboard", id="leaderboard-header"),
            DataTable(id="leaderboard", classes="centered-table"),
            id="right-pane",
        )

    def on_mount(self):
        # Configure the leaderboard table
        leaderboard = self.query_one("#leaderboard", DataTable)
        leaderboard.add_columns("  Rank  ", "  Username  ", "  WPM  ", "  Accuracy  ")
        self.update_leaderboard()

    def update_leaderboard(self):
        leaderboard = self.query_one("#leaderboard", DataTable)
        leaderboard.clear()
        records = self.db.fetch_records()

        # Sort by WPM in descending order
        sorted_records = sorted(records, key=lambda x: -x[1])

        # Populate the leaderboard
        if sorted_records:
            for rank, record in enumerate(sorted_records, start=1):
                leaderboard.add_row(
                    Text(str(rank), justify="center"),
                    Text(record[0], justify="center"),  # Username
                    Text(f"{record[1]:.2f}", justify="center"),  # WPM (correct words only)
                    Text(f"{record[2]:.2f}%", justify="center")  # Accuracy (optional, can be removed)
                )

    def on_input_submitted(self, event: Input.Submitted):
        if event.input.id == "username-input":
            self.username = event.input.value.strip()
            if not self.username:
                return

            # Hide username input and label
            event.input.add_class("hidden")
            self.query_one("#username-label", Static).add_class("hidden")

            # Show countdown label
            countdown_label = self.query_one("#countdown-label", Static)
            countdown_label.remove_class("hidden")
            self.countdown_value = 3
            countdown_label.update(Text(f"{self.countdown_value}", style='bold'))

            # Start countdown
            self.countdown_timer = self.set_interval(1, self.run_countdown, repeat=3)

            event.input.clear()

        elif event.input.id == "typing-input":
            self.typed_text = event.input.value.strip()
            elapsed_time = self.get_time() - self.start_time

            # Calculate WPM based on correct words
            wpm = calculate_wpm(self.sample_text.plain, self.typed_text, elapsed_time)
            accuracy = calculate_accuracy(self.sample_text.plain, self.typed_text)

            # Save the record and reset
            player = Player(self.username)
            self.db.save_record(player.username, wpm, accuracy)
            self.update_leaderboard()

            self.start_time = None

            # Hide typing input and label
            event.input.add_class("hidden")
            self.query_one("#text-label", Static).add_class("hidden")

            # Hide text-to-type widget
            text_to_type = self.query_one("#text-to-type", Static)
            text_to_type.add_class("hidden")

            # Show username input and label
            username_input = self.query_one("#username-input", Input)
            username_label = self.query_one("#username-label", Static)
            username_input.remove_class("hidden")
            username_label.remove_class("hidden")

            # Generate a new sample text for the next user
            self.sample_text = self.generate_sample_text()
            self.query_one("#text-to-type", Static).update(self.sample_text)

            event.input.clear()

            countdown_label = self.query_one("#countdown-label", Static)
            countdown_label.add_class("hidden")

    def run_countdown(self):
        countdown_label = self.query_one("#countdown-label", Static)
        if self.countdown_value > 1:
            self.countdown_value -= 1
            countdown_label.update(Text(f"{self.countdown_value}", style='bold'))
        elif self.countdown_value == 1:
            self.countdown_value = 0
            countdown_label.update(Text("Go!", style='bold'))

            # Stop the countdown timer
            self.countdown_timer.stop()

            # Show text-to-type widget
            text_to_type = self.query_one("#text-to-type", Static)
            text_to_type.remove_class("hidden")

            # Show typing input and label
            typing_input = self.query_one("#typing-input", Input)
            typing_label = self.query_one("#text-label", Static)
            typing_input.remove_class("hidden")
            typing_label.remove_class("hidden")

            # Start the timer
            self.start_time = self.get_time()
            typing_input.focus()

    @staticmethod
    def get_time():
        import time
        return time.time()
