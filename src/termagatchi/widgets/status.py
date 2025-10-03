"""Status bars widget for displaying pet stats."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, Grid
from textual.widgets import ProgressBar, Static

from ..engine.models import PetStats


class StatusBar(Vertical):
    """A single status bar with label and progress using ProgressBar widget."""

    def __init__(self, label: str, value: float = 50.0, color: str = "white", **kwargs):
        super().__init__(**kwargs)
        self.label = label
        self.value = value
        self.color = color

    def compose(self) -> ComposeResult:
        """Compose the status bar layout."""
        yield Static(self.label.upper(), classes="status-label")
        yield ProgressBar(total=100, show_eta=False, show_percentage=False)

    def on_mount(self) -> None:
        """Initialize status bar when mounted."""
        self.add_class("status-bar")
        self.add_class(f"{self.label.lower()}-bar")
        self.update_value(self.value)

    def update_value(self, value: float) -> None:
        """Update the progress bar value."""
        self.value = max(0.0, min(100.0, value))
        # Find the ProgressBar child and update it
        try:
            progress_bar = self.query_one(ProgressBar)
            progress_bar.update(progress=self.value)
            print(f"DEBUG: Updated {self.label} to {self.value}%")
        except Exception as e:
            print(f"DEBUG: Error updating {self.label}: {e}")


class StatusPanel(Static):
    """Panel containing all status bars."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        """Compose the status panel layout."""
        # Use Grid container for proper layout
        from textual.containers import Grid
        with Grid(id="status-grid"):
            yield StatusBar("HUNGER", 75.0, classes="hunger-bar")
            yield StatusBar("HAPPINESS", 85.0, classes="happiness-bar")
            yield StatusBar("ENERGY", 60.0, classes="energy-bar")

    def on_mount(self) -> None:
        """Initialize status bars after mounting."""
        pass

    def update_stats(self, stats: PetStats) -> None:
        """Update all status bars with current stats."""
        print(f"DEBUG: Updating stats - Hunger: {stats.hunger}, Happiness: {stats.happiness}, Energy: {stats.energy}")
        # Get status bars and update them
        status_bars = self.query(StatusBar)
        print(f"DEBUG: Found {len(status_bars)} status bars")
        if len(status_bars) >= 3:
            status_bars[0].update_value(stats.hunger)
            status_bars[1].update_value(stats.happiness)
            status_bars[2].update_value(stats.energy)
        else:
            print("DEBUG: Not enough status bars found!")
