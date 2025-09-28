"""Status bars widget for displaying pet stats."""

from textual.widgets import Static, ProgressBar
from textual.containers import Horizontal
from textual.app import ComposeResult

from ..engine.models import PetStats


class StatusBar(Static):
    """A single status bar with label and progress."""

    def __init__(self, label: str, value: float = 50.0, color: str = "white", **kwargs):
        super().__init__(**kwargs)
        self.label = label
        self.value = value
        self.color = color
        self.progress_bar = ProgressBar(total=100, show_percentage=False)

    def compose(self) -> ComposeResult:
        """Compose the status bar layout."""
        yield Static(self.label.upper(), classes="status-label")
        yield self.progress_bar

    def update_value(self, value: float) -> None:
        """Update the progress bar value."""
        self.value = max(0.0, min(100.0, value))
        self.progress_bar.progress = self.value

        # Update styling based on value
        if self.value < 20:
            self.progress_bar.styles.bar_color = "red"
        elif self.value < 40:
            self.progress_bar.styles.bar_color = "yellow"
        else:
            self.progress_bar.styles.bar_color = self.color


class StatusPanel(Static):
    """Panel containing all status bars."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hunger_bar = StatusBar("Hunger", color="orange")
        self.happiness_bar = StatusBar("Happiness", color="green")
        self.energy_bar = StatusBar("Energy", color="orange")

    def compose(self) -> ComposeResult:
        """Compose the status panel layout."""
        with Horizontal(classes="status-bars"):
            yield self.hunger_bar
            yield self.happiness_bar
            yield self.energy_bar

    def update_stats(self, stats: PetStats) -> None:
        """Update all status bars with current stats."""
        self.hunger_bar.update_value(stats.hunger)
        self.happiness_bar.update_value(stats.happiness)
        self.energy_bar.update_value(stats.energy)

        # Update the display
        self.refresh()

    def on_mount(self) -> None:
        """Initialize status bars when mounted."""
        self.add_class("status-panel")
        # Set initial styles
        self.hunger_bar.add_class("hunger-bar")
        self.happiness_bar.add_class("happiness-bar")
        self.energy_bar.add_class("energy-bar")