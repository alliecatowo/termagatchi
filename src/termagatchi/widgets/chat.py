"""Chat log widget for displaying conversation history."""

from datetime import datetime
from typing import Any

from rich.text import Text
from textual.app import ComposeResult
from textual.widgets import RichLog, Static


class ChatLog(Static):
    """Widget for displaying chat history between user and pet."""

    def __init__(self, max_lines: int = 100, **kwargs):
        super().__init__(**kwargs)
        self.max_lines = max_lines
        self._log = RichLog(highlight=True, markup=True)

    def compose(self) -> ComposeResult:
        """Compose the chat log widget."""
        yield self._log

    def on_mount(self) -> None:
        """Initialize the chat log."""
        self.add_class("chat-log")
        self._log.add_class("chat-log-content")

    def add_user_message(self, message: str) -> None:
        """Add a user message to the chat log."""
        timestamp = datetime.now().strftime("%H:%M")

        # Create styled user message
        user_text = Text()
        user_text.append(f"[{timestamp}] ", style="dim")
        user_text.append("you: ", style="#4fc3f7 bold")
        user_text.append(message, style="#4fc3f7")

        self._log.write(user_text)
        self._scroll_to_bottom()

    def add_pet_message(self, message: str, action: str = "") -> None:
        """Add a pet message to the chat log."""
        timestamp = datetime.now().strftime("%H:%M")

        # Create styled pet message
        pet_text = Text()
        pet_text.append(f"[{timestamp}] ", style="dim")
        pet_text.append("tama: ", style="#ffd700 bold")
        pet_text.append(message, style="#ffd700")

        if action:
            pet_text.append(f" *{action.lower()}*", style="#ffd700 italic")

        self._log.write(pet_text)
        self._scroll_to_bottom()

    def add_system_message(self, message: str) -> None:
        """Add a system message to the chat log."""
        timestamp = datetime.now().strftime("%H:%M")

        # Create styled system message
        system_text = Text()
        system_text.append(f"[{timestamp}] ", style="dim")
        system_text.append("* ", style="dim")
        system_text.append(message, style="dim italic")
        system_text.append(" *", style="dim")

        self._log.write(system_text)
        self._scroll_to_bottom()

    def add_error_message(self, message: str) -> None:
        """Add an error message to the chat log."""
        timestamp = datetime.now().strftime("%H:%M")

        # Create styled error message
        error_text = Text()
        error_text.append(f"[{timestamp}] ", style="dim")
        error_text.append("ERROR: ", style="red bold")
        error_text.append(message, style="red")

        self._log.write(error_text)
        self._scroll_to_bottom()

    def load_chat_history(self, history: list[dict[str, Any]]) -> None:
        """Load chat history from saved data."""
        self._log.clear()

        for entry in history[-20:]:  # Show last 20 messages
            sender = entry.get("sender", "unknown")
            message = entry.get("message", "")
            timestamp_str = entry.get("timestamp", "")

            try:
                # Parse timestamp if available
                if timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str)
                    time_str = timestamp.strftime("%H:%M")
                else:
                    time_str = "??:??"
            except ValueError:
                time_str = "??:??"

            if sender == "user":
                text = Text()
                text.append(f"[{time_str}] ", style="dim")
                text.append("you: ", style="#4fc3f7 bold")
                text.append(message, style="#4fc3f7")
                self._log.write(text)

            elif sender == "pet":
                text = Text()
                text.append(f"[{time_str}] ", style="dim")
                text.append("tama: ", style="#ffd700 bold")
                text.append(message, style="#ffd700")
                self._log.write(text)

            elif sender == "system":
                text = Text()
                text.append(f"[{time_str}] ", style="dim")
                text.append("* ", style="dim")
                text.append(message, style="dim italic")
                text.append(" *", style="dim")
                self._log.write(text)

        self._scroll_to_bottom()

    def clear_chat(self) -> None:
        """Clear all messages from the chat log."""
        self._log.clear()

    def _scroll_to_bottom(self) -> None:
        """Scroll the log to the bottom to show latest messages."""
        # The RichLog widget automatically scrolls to bottom on new content
        pass

    def get_visible_line_count(self) -> int:
        """Get the number of visible lines in the chat log."""
        # TODO: Fix accessing private _content attribute - use proper API
        return len(self._log._content)
