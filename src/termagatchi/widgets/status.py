"""Status bars widget for displaying pet stats."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, Grid
from textual.widgets import ProgressBar, Static

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

        # TODO: Update styling based on value when we fix CSS approach
        # Currently Textual ProgressBar doesn't support dynamic bar_color
        # Will need to use CSS classes for different value ranges


class StatusPanel(Static):
    """Panel containing all status bars."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hunger_bar = StatusBar("Hunger", color="#ff8c42")
        self.happiness_bar = StatusBar("Happiness", color="#4caf50")
        self.energy_bar = StatusBar("Energy", color="#ffeb3b")
        self.hygiene_bar = StatusBar("Hygiene", color="#2196f3")
        self.affection_bar = StatusBar("Affection", color="#e91e63")
        self.health_bar = StatusBar("Health", color="#4caf50")

    def compose(self) -> ComposeResult:
        """Compose the status panel layout."""
        with Grid(classes="status-bars"):
            yield self.hunger_bar
            yield self.happiness_bar
            yield self.energy_bar
            yield self.hygiene_bar
            yield self.affection_bar
            yield self.health_bar

    def update_stats(self, stats: PetStats) -> None:
        """Update all status bars with current stats."""
        self.hunger_bar.update_value(stats.hunger)
        self.happiness_bar.update_value(stats.happiness)
        self.energy_bar.update_value(stats.energy)
        self.hygiene_bar.update_value(stats.hygiene)
        self.affection_bar.update_value(stats.affection)
        self.health_bar.update_value(stats.health)

        # Update the display
        self.refresh()

    def on_mount(self) -> None:
        """Initialize status bars when mounted."""
        self.add_class("status-panel")
        # Set initial styles
        self.hunger_bar.add_class("hunger-bar")
        self.happiness_bar.add_class("happiness-bar")
        self.energy_bar.add_class("energy-bar")
        self.hygiene_bar.add_class("hygiene-bar")
        self.affection_bar.add_class("affection-bar")
        self.health_bar.add_class("health-bar")
