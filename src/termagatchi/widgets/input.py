"""Input widget for user commands and messages."""

from textual.widgets import Input, Static
from textual.containers import Horizontal
from textual.app import ComposeResult
from textual.message import Message


class CommandInput(Static):
    """Input widget for commands and chat messages."""

    class Submitted(Message):
        """Message sent when input is submitted."""

        def __init__(self, value: str, is_command: bool) -> None:
            self.value = value
            self.is_command = is_command
            super().__init__()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.input_field = Input(placeholder="Type a message or /command...")

    def compose(self) -> ComposeResult:
        """Compose the input widget."""
        with Horizontal(classes="input-container"):
            yield Static("> ", classes="input-prompt")
            yield self.input_field

    def on_mount(self) -> None:
        """Initialize the input widget."""
        self.add_class("command-input")
        self.input_field.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        value = event.value.strip()
        if not value:
            return

        # Determine if this is a command
        is_command = value.startswith("/")

        # Clear the input
        self.input_field.value = ""

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
            "/quit"
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