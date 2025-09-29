"""Input widget for user commands and messages."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widgets import Input, Static
from textual.widget import Widget


class CommandInput(Static):
    """Input widget for commands and chat messages with autocomplete."""

    class Submitted(Message):
        """Message sent when input is submitted."""

        def __init__(self, value: str, is_command: bool) -> None:
            self.value = value
            self.is_command = is_command
            super().__init__()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.input_field = Input(placeholder="Type a message or /command...")
        self.available_commands = [
            "/feed", "/clean", "/play", "/sleep", "/pet", "/status", "/save", "/quit"
        ]
        self.completion_container = None
        self.showing_completions = False

    def compose(self) -> ComposeResult:
        """Compose the input widget."""
        with Vertical():
            yield self.input_field
            # Container for autocomplete suggestions
            self.completion_container = Vertical(id="completions")
            yield self.completion_container

    def on_mount(self) -> None:
        """Initialize the input widget."""
        self.add_class("command-input")
        self.input_field.focus()

    def on_key(self, event) -> None:
        """Handle key events for autocomplete."""
        if event.key == "tab" and self.showing_completions:
            # Auto-complete with first suggestion
            completions = self.get_completions()
            if completions:
                self.input_field.value = completions[0]
                self.input_field.cursor_position = len(completions[0])
                self.hide_completions()
                event.prevent_default()
        elif event.key == "escape":
            # Hide completions
            self.hide_completions()
        elif event.key in ("up", "down") and self.showing_completions:
            # Navigate completions
            self.navigate_completions(1 if event.key == "down" else -1)
            event.prevent_default()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes to show autocomplete."""
        value = event.value
        if value.startswith("/"):
            self.show_completions(value)
        else:
            self.hide_completions()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        value = event.value.strip()
        if not value:
            return

        # Determine if this is a command
        is_command = value.startswith("/")

        # Clear the input
        self.input_field.value = ""

        # Hide completions
        self.hide_completions()

        # Post our custom message
        self.post_message(self.Submitted(value, is_command))

    def focus_input(self) -> None:
        """Focus the input field."""
        self.input_field.focus()

    def set_placeholder(self, text: str) -> None:
        """Set the input placeholder text."""
        self.input_field.placeholder = text

    def get_input_value(self) -> str:
        """Get the current input value."""
        return self.input_field.value

    def set_input_value(self, value: str) -> None:
        """Set the input value."""
        self.input_field.value = value

    def get_completions(self) -> list[str]:
        """Get command completions for current input."""
        value = self.input_field.value
        if not value.startswith("/"):
            return []

        # Find commands that start with the current input
        completions = []
        for command in self.available_commands:
            if command.startswith(value):
                completions.append(command)

        return completions

    def show_completions(self, current_value: str) -> None:
        """Show autocomplete suggestions."""
        completions = self.get_completions()
        if not completions:
            self.hide_completions()
            return

        self.completion_container.remove_children()

        # Add completion items
        for i, completion in enumerate(completions[:5]):  # Show max 5 suggestions
            item = Static(completion, classes=f"completion-item {'selected' if i == 0 else ''}")
            self.completion_container.mount(item)

        self.showing_completions = True

    def hide_completions(self) -> None:
        """Hide autocomplete suggestions."""
        self.completion_container.remove_children()
        self.showing_completions = False

    def navigate_completions(self, direction: int) -> None:
        """Navigate through completions with arrow keys."""
        if not self.showing_completions:
            return

        items = self.completion_container.query(".completion-item")
        if not items:
            return

        # Find currently selected item
        selected_index = 0
        for i, item in enumerate(items):
            if "selected" in item.classes:
                selected_index = i
                break

        # Remove selected class from all items
        for item in items:
            item.remove_class("selected")

        # Add selected class to new item
        new_index = max(0, min(len(items) - 1, selected_index + direction))
        items[new_index].add_class("selected")


class CommandsPanel(Static):
    """Panel showing available commands."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.commands = [
            "/feed [item]",
            "/clean [item]",
            "/play [item]",
            "/sleep [on|off]",
            "/pet",
            "/status",
            "/save",
            "/quit",
        ]

    def compose(self) -> ComposeResult:
        """Compose the commands panel."""
        yield Static("COMMANDS", classes="command-title")

        for command in self.commands:
            yield Static(command, classes="command-item")

    def on_mount(self) -> None:
        """Initialize the commands panel."""
        self.add_class("commands-panel")

    def update_commands(self, commands: list[str]) -> None:
        """Update the list of available commands."""
        self.commands = commands

        # Remove existing command items
        for child in self.children[1:]:  # Skip the title
            child.remove()

        # Add new command items
        for command in self.commands:
            self.mount(Static(command, classes="command-item"))

    def highlight_command(self, command: str) -> None:
        """Highlight a specific command temporarily."""
        # This could be implemented to provide visual feedback
        pass
